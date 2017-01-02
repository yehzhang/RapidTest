from collections import defaultdict
from json import JSONDecoder, dumps
from socket import socket
from threading import Lock, Thread, Condition

from .._compat import queue


class ExecutionRPCClient(object):
    _count_requests = 0

    TIMEOUT = 10
    RECEIVE_TIMEOUT = 10

    METHOD_EXECUTE = 'execute'
    METHOD_TERMINATE = 'terminate'
    WHO_I_AM = 'target'

    def __init__(self, addr, obj_types):
        """
        :param (str, int) addr:
        :param {str: type} obj_types:
        """
        self.acceptor = None
        self.addr = addr
        self.decoder = JSONDecoder(object_hook=self._get_object_hook_handler(obj_types))

        self.sending_channels_lock = Lock()
        self.receiving_channels_lock = Lock()
        self._reset_channels()

    def __del__(self):
        self.close()

    def run(self):
        """
        :return (str, int): address of socket
        """
        if self.acceptor is None:
            self.acceptor = Acceptor(self)
        return self.acceptor.get_address()

    def close(self):
        if self.acceptor is not None:
            self.acceptor.close()
            self.acceptor = None
            self._reset_channels()

    def _reset_channels(self):
        # {str: Queue}: {target: channel}
        self.sending_channels = defaultdict(queue.Queue)
        self.receiving_channels = defaultdict(queue.Queue)

    def request(self, target, request):
        """Send request and wait for response.

        :param str target:
        :param Request request:
        :return Response:
        """
        request.id = self.new_id()
        self._send(target, request)

        return self._receive(target)

    def notify(self, target, request):
        """Send request and return immediately.

        :param str target:
        :param Request request:
        """
        if request.id is not None:
            raise ValueError('Notification has id')
        self._send(target, request)

    def _send(self, target, request):
        s = self.acceptor.get_sender(target)
        s.raise_()
        if s.closed():
            raise RuntimeError('Connection already closed')

        self.acceptor.get_sender(target).raise_()
        with self.sending_channels_lock:
            channel = self.sending_channels[target]
        channel.put_nowait(request)

    def _receive(self, target):
        r = self.acceptor.get_receiver(target)
        r.raise_()
        if r.closed():
            raise RuntimeError('Connection already closed')

        with self.receiving_channels_lock:
            channel = self.receiving_channels[target]
        try:
            return channel.get(True, self.RECEIVE_TIMEOUT)
        except queue.Empty:
            raise RuntimeError('Target did not respond in time')

    def get_sending_channel(self, target):
        """Thread-safe

        :param str target:
        :return Queue:
        """
        with self.sending_channels_lock:
            return self.sending_channels[target]

    def get_receiving_channel(self, target):
        """Thread-safe

        :param str target:
        :return Queue:
        """
        with self.receiving_channels_lock:
            return self.receiving_channels[target]

    def close_channels(self, target):
        """Thread-safe

        :param str target:
        """
        with self.sending_channels_lock, self.receiving_channels_lock:
            self.sending_channels.pop(target, None)
            self.receiving_channels.pop(target, None)

    @classmethod
    def _get_object_hook_handler(cls, obj_types):
        def _object_hook_handler(d):
            ctor_pair = d.pop('__jsonclass__', None)
            if ctor_pair is not None:
                ctor_name, params = ctor_pair
                if ctor_name not in obj_types:
                    raise NameError('name {} is not defined'.format(repr(ctor_name)))
                obj = obj_types[ctor_name](*params)
                for k, v in d.items():
                    setattr(obj, k, v)
            else:
                obj = d
            return obj

        return _object_hook_handler

    @classmethod
    def new_id(cls):
        _id = '{}_client_request_{}'.format(cls.__name__, cls._count_requests)
        cls._count_requests += 1
        return _id


class Dictable(object):
    def __iter__(self):
        for item in self.__dict__.items():
            yield item


class Request(Dictable):
    """Request in JSON-RPC"""

    def __init__(self, method=None, params=None, _id=None):
        self.method = method
        self.params = params
        self.id = _id


class Response(Dictable):
    """Response in JSON-RPC"""

    def __init__(self, result=None, error=None, _id=None):
        self.result = result
        self.error = error
        self.id = _id


class ExcThread(Thread):
    def __init__(self, *args, **kwargs):
        super(ExcThread, self).__init__(*args, **kwargs)

        self.exception = None

    def run(self):
        try:
            super(ExcThread, self).run()
        except Exception as e:
            self.exception = e

    def raise_(self):
        if self.exception:
            raise self.exception


class SocketWorker(object):
    def __init__(self, client, socket):
        self.client = client
        self.socket = socket
        self.closed = False
        t = self.thread = self._create_thread()
        t.start()

    def __del__(self):
        self.close()

    def close(self):
        self.socket.close()
        self.thread.join()
        self.closed = True

    def raise_(self):
        self.thread.raise_()

    def _create_thread(self):
        def _auto_close():
            try:
                self.handle()
            finally:
                self.close()

        return ExcThread(target=_auto_close)

    def handle(self):
        raise NotImplementedError

    def _read(self, s=None):
        s = s or self.socket

        data = []
        while True:
            d = s.recv(4096)
            if not d:
                break
            data.append(d.decode())
        data = ''.join(data)

        if not data:
            return None
        obj = self.client.decoder.decode(data)
        return Request(**obj)

    def get_address(self):
        return self.socket.getsockname()

    def closed(self):
        return self.closed


class Acceptor(SocketWorker):
    def __init__(self, client):
        s = socket()
        s.bind(client.addr)
        s.listen(5)

        super(Acceptor, self).__init__(client, s)

        self.workers_lock = Lock()
        self.workers = {}
        self.worker_created = Condition(self.workers_lock)

    def handle(self):
        while True:
            # Accept
            conn, _ = self.socket.accept()
            request = self._read(conn)
            if request is None:
                break

            s = Sender(self, request, conn)
            r = Receiver(self, request, conn)
            with self.workers_lock:
                self.workers[r.target] = s, r
                self.worker_created.notify_all()

        for s, r in self.workers.values():
            r.close()
            s.close()

    def close(self):
        closer = socket()
        closer.connect(self.get_address())
        closer.close()

        super(Acceptor, self).close()

    def _get_workers(self, target):
        with self.workers_lock:
            while target not in self.workers:
                self.worker_created.wait()
            workers = self.workers[target]
        if workers is None:
            raise RuntimeError('Connection is already closed.')
        return workers

    def remove_workers(self, target):
        with self.workers_lock:
            if target not in self.workers:
                raise RuntimeError('Connection does not exist.')
            self.workers[target] = None

    def get_receiver(self, target):
        _, r = self._get_workers(target)
        return r

    def get_sender(self, target):
        s, _ = self._get_workers(target)
        return s

    def get_worker_address(self, target):
        return self.get_receiver(target).get_address()


class Communicator(SocketWorker):
    def __init__(self, acceptor, request, socket):
        self.acceptor = acceptor
        self.target = request.params[acceptor.client.WHO_I_AM]

        super(Communicator, self).__init__(acceptor.client, socket)


class Sender(Communicator):
    def handle(self):
        sendings_queue = self.client.get_sending_channel(self.target)

        while True:
            # Send
            sending = sendings_queue.get(True)
            if sending is None:
                break

            data = dumps(dict(sending))
            self.socket.sendall(data)

            if isinstance(sending, Request) and sending.method is self.client.METHOD_TERMINATE:
                break


class Receiver(Communicator):
    def handle(self):
        try:
            receivings_queue = self.client.get_receiving_channel(self.target)

            while True:
                # Receive
                receiving = self._read()
                if receiving is None:
                    break
                receivings_queue.put_nowait(receiving)

        finally:
            self.client.close_channels(self.target)
            self.client.remove_workers(self.target)
