from json import JSONDecoder, JSONEncoder
from select import select
from socket import socket
from threading import Lock, Thread, Condition

from .._compat import queue, raise_from
from ..utils import Dictable, natural_join


class ExecutionRPCClient(object):
    _count_requests = 0

    RECEIVE_TIMEOUT = 10000  # TODO
    # RECEIVE_TIMEOUT = 10

    METHOD_HELLO = 'hello'  # first server send to client a notification with target_id as params
    METHOD_EXECUTE = 'execute'
    METHOD_TERMINATE = 'terminate'
    WHO_I_AM = 'target'

    def __init__(self, addr, obj_types):
        """
        :param Tuple[str, int] addr:
        :param Dict[str, type] obj_types:
        """
        self.acceptor = None
        self.addr = addr
        self.decoder = JSONDecoder(object_hook=self._get_object_hook_handler(obj_types))
        self.encoder = JSONEncoder(separators=(',', ':'))

    def __del__(self):
        self.close()

    def run(self):
        """
        :return Tuple[str, int]: address of socket
        """
        if self.acceptor is None:
            self.acceptor = Acceptor(self)
            self.addr = self.acceptor.get_address()
        return self.addr

    def close(self):
        if self.acceptor is not None:
            ator = self.acceptor
            ator.close()
            ator.join()
            self.acceptor = None
            ator.raise_()

    def request(self, target, method, params):
        """Send request and wait for response.

        :param Any target:
        :param str method:
        :param List[Any] params:
        :return Response:
        """
        request = Request(method, params, self.new_id())
        self._send(target, request)
        return self._receive(target)

    def notify(self, target, method, params):
        """Send notification and return immediately.

        :param Any target:
        :param str method:
        :param List[Any] params:
        """
        request = Request(method, params)
        self._send(target, request)

    def _send(self, target, request):
        s = self.acceptor.get_sender(target)
        s.send(request)

    def _receive(self, target):
        # TODO add id argument
        r = self.acceptor.get_receiver(target)
        try:
            receiving = r.receive(self.RECEIVE_TIMEOUT)
        except queue.Empty:
            # TODO send timeout to target so that I can tell IOError from TLE. Or is that important?
            raise_from(RuntimeError('target did not respond in time'), None)
        else:
            # TODO should keep receivings separate if it is not a response to this request (same id)
            # or a notification
            if isinstance(receiving, Exception):
                raise receiving
            else:
                error = getattr(receiving, 'error', None)
                if error:
                    msg = 'exception raised while executing external target'
                    ExcWrapper, exc = error.to_exception()
                    raise_from(ExcWrapper(msg), exc)
            return receiving

    @classmethod
    def _get_object_hook_handler(cls, obj_types):
        def _object_hook_handler(d):
            ctor_pair = d.pop('__jsonclass__', None)
            if ctor_pair is not None:
                ctor_name, params = ctor_pair
                if ctor_name not in obj_types:
                    raise NameError('name {} is not defined'.format(repr(ctor_name)))
                T = obj_types[ctor_name]
                if isinstance(params, dict):
                    obj = T(**params)
                else:
                    obj = T(*params)
                for k, v in d.items():
                    setattr(obj, k, v)
            else:
                obj = d
            return obj

        return _object_hook_handler

    @classmethod
    def new_id(cls):
        _id = '{}:request:{}'.format(cls.__name__, cls._count_requests)
        cls._count_requests += 1
        return _id


class Request(Dictable):
    """Request in JSON-RPC"""

    def __init__(self, method=None, params=None, id=None):
        self.method = method
        self.params = params
        self.id = id


class Response(Dictable):
    """Response in JSON-RPC"""

    def __init__(self, result=None, error=None, id=None):
        self.result = result
        self.error = error
        self.id = id


class ThreadedSocketWorker(object):
    _count_workers = 0

    def __init__(self, client, socket):
        self.id = self._count_workers
        ThreadedSocketWorker._count_workers += 1
        self.client = client
        self.socket = socket

        self._read_buf = ''

        self._working = False
        self.exception = None
        self.thread = self._start_thread()

    def __del__(self):
        self.close()

    def close(self):
        print('{} closed.'.format(type(self).__name__))
        self.socket.close()

    def join(self, timeout=None):
        self.thread.join(timeout)

    def raise_(self):
        if self.exception:
            e = self.exception
            self.exception = None
            raise e

    def _start_thread(self):
        def _auto_close():
            self._working = True
            try:
                self.handle()
            except BaseException as e:
                # Store exception raised in child thread
                import traceback
                print('Worker ends with exception: ' + traceback.format_exc())
                self.exception = e
            finally:
                self._working = False
                self.close()

        t = Thread(target=_auto_close, name=self.get_name())
        t.daemon = True
        t.start()
        return t

    def get_name(self):
        return '{}-{}'.format(type(self).__name__, self.id)

    def handle(self):
        raise NotImplementedError

    def _read(self, s=None):
        """
        :param socket s:
        :return Request|Response:
        """
        s = s or self.socket

        length = None
        buf = self._read_buf
        while True:
            # A rpc starts with its length and a space. Get that
            if length is None:
                str_length, sep, content = buf.partition(' ')
                if sep:
                    length = int(str_length)
                    buf = content

            if length is not None and len(buf) >= length:
                # Read everything in this call
                break

            d = None
            try:
                r, _, _ = select([s], [], [])
            except IOError:
                import traceback
                traceback.print_exc()
                pass
            else:
                if r:
                    d = s.recv(4096).decode()
            if not d:
                # Socket is probably closed before data is fully transmitted.
                # Discard everything as if nothing was received.
                buf = ''
                break
            buf += d
        # Store unconsumed buf, if any
        self._read_buf = buf[length:]

        if length == 0:
            return None
        obj = self.client.decoder.decode(buf[:length])
        print('Python received data: {}'.format(obj))
        if isinstance(obj, dict):
            for T in (Response, Request):
                try:
                    return T(**obj)
                except TypeError:
                    pass
        raise ValueError('received data is invalid')

    def _send(self, sending):
        """
        :param Any sending: better be of Request|Response
        """
        data = self.client.encoder.encode(dict(sending))
        self.socket.send('{} '.format(len(data)).encode())
        self.socket.send(data.encode())
        print('Python send: ' + data)

    def get_address(self):
        return self.socket.getsockname()

    def _ensure_working(self):
        if not self._working:
            raise RuntimeError('connection already closed')


class Acceptor(ThreadedSocketWorker):
    def __init__(self, client):
        s = socket()
        s.bind(client.addr)
        s.listen(5)

        super(Acceptor, self).__init__(client, s)

        self.workers_lock = Lock()
        self.workers = {}
        self.worker_created = Condition(self.workers_lock)
        self.closed_workers = []

    def handle(self):
        while True:
            # Accept
            conn, _ = self.socket.accept()
            print('Python accept from: {}:{}'.format(*_))
            request = self._read(conn)
            if request is None:
                break
            if request.method != self.client.METHOD_HELLO:
                # Raise an exception for now
                raise RuntimeError('Initial request of a connection was invalid')

            target = request.params[0]
            r = Receiver(self, target, conn)
            s = Sender(self, target, conn)
            with self.workers_lock:
                self.workers[target] = r, s
                self.worker_created.notify_all()

        for r, s in self.workers.values():
            r.close()
            s.close()
            print('workers joined')

    def close(self):
        # Accepting socket is a little hard to close
        # TODO any better idea?
        closer = socket()
        try:
            closer.connect(self.get_address())
        except OSError:
            pass
        else:
            closer.close()

        super(Acceptor, self).close()

    def _get_workers(self, target):
        with self.workers_lock:
            while target not in self.workers:
                self.worker_created.wait()
            workers = self.workers[target]
        if workers is None:
            raise RuntimeError('connection is already closed.')
        return workers

    def remove_workers(self, target):
        with self.workers_lock:
            # if target not in self.workers:
            #     raise RuntimeError('connection does not exist.')
            self.workers[target] = None

    def get_receiver(self, target):
        r, _ = self._get_workers(target)
        return r

    def get_sender(self, target):
        _, s = self._get_workers(target)
        return s


# noinspection PyAbstractClass
class Communicator(ThreadedSocketWorker):
    def __init__(self, acceptor, target, socket):
        self.target = target

        super(Communicator, self).__init__(acceptor.client, socket)

        self.acceptor = acceptor
        self.channel = queue.Queue()

    def close(self):
        self.acceptor.remove_workers(self.target)

        items = []
        while not self.channel.empty():
            items.append(self.channel.get())
        print('{} closed. In channel: {}'.format(type(self).__name__,
                                                 natural_join('and', map(repr, items))))

        super(Communicator, self).close()

    def get_name(self):
        return '{}:{}'.format(super(Communicator, self).get_name(), self.target)

    def _non_worker_thread_channel(self):
        """Make sure exception is passed to the main thread and prevents deadlock."""
        self.raise_()
        self._ensure_working()
        return self.channel


class Sender(Communicator):
    def send(self, data):
        """Send data to target. Thread-safe.

        :param Request|Response|None data: None means stop the sender
        """
        assert isinstance(data, Dictable) or data is None
        self._non_worker_thread_channel().put_nowait(data)

    def handle(self):
        while True:
            sending = self.channel.get(True)
            if sending is None:
                break
            self._send(sending)
            if getattr(sending, 'method', None) is self.client.METHOD_TERMINATE:
                break


class Receiver(Communicator):
    def receive(self, timeout=None):
        """Receive the next transmission from target. Thread-safe.

        :return Request|Response:
        """
        return self._non_worker_thread_channel().get(True, timeout)

    def handle(self):
        try:
            while True:
                receiving = self._read()
                if receiving is None:
                    raise RuntimeError('nothing to receive')
                self.channel.put_nowait(receiving)
        except Exception as e:
            self.channel.put_nowait(e)
