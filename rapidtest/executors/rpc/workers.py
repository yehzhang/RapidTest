from select import select
from socket import socket
from threading import Lock, Thread, Condition

from .exceptions import TimeoutError
from .utils import Request, Response
from ..._compat import queue
from ...utils import Dictable, natural_join


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
                print(
                    'Worker {} ends with exception: {}'.format(self, traceback.format_exc()))
                self.exception = e
            finally:
                self._working = False
                self.close()

        t = Thread(target=_auto_close, name=str(self))
        t.daemon = True
        t.start()
        return t

    def __str__(self):
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
            except OSError:
                import traceback
                traceback.print_exc()
                pass
            else:
                if r:
                    d = s.recv(4096).decode()
            if not d:
                # Socket is probably closed before data is fully transmitted.
                # Discard everything as if nothing was received.
                length = 0
                buf = ''
                break
            buf += d
        # Store unconsumed buf, if any
        self._read_buf = buf[length:]

        assert isinstance(length, int)
        if length == 0:
            return None
        print('Python received {} data: {}'.format(length, repr(buf[:length])))
        obj = self.client.decoder.decode(buf[:length])
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
            print('Python created communicators: {}, {}'.format(r, s))
            with self.workers_lock:
                self.workers[target] = r, s
                self.worker_created.notify_all()

        print('Workers to remove: {}'.format(self.workers))
        for target in self.workers:
            self.remove_workers(target)

    def close(self):
        # Accepting socket is a little hard to close
        # # TODO any better idea?
        # closer = socket()
        # try:
        #     closer.connect(self.get_address())
        # except OSError:
        #     pass
        # else:
        #     closer.close()

        super(Acceptor, self).close()

    # noinspection PyUnboundLocalVariable
    def get_workers(self, target, timeout=None):
        """
        :param Any target:
        :param int timeout:
        :return Tuple[Communicator, Communicator]: (receiver, sender)
        """
        with self.workers_lock:
            if timeout is None:
                while target not in self.workers:
                    self.worker_created.wait()
            else:
                self.worker_created.wait(timeout)
                if target not in self.workers:
                    raise TimeoutError('target did not connect in time')
            workers = self.workers[target]
        if workers is None:
            raise RuntimeError('connection is already closed.')
        return workers

    # noinspection PyUnboundLocalVariable
    def remove_workers(self, target):
        """Remove workers to release memory. Server calls this method when no longer communications
            with target. """
        with self.workers_lock:
            if target not in self.workers:
                raise RuntimeError('connection does not exist.')
            r, s = self.workers[target]
            self.workers[target] = None

        r.close()
        s.close()
        r.join()
        s.join()


# noinspection PyAbstractClass
class Communicator(ThreadedSocketWorker):
    def __init__(self, acceptor, target, socket):
        self.target = target
        self.channel = queue.Queue()
        self.acceptor = acceptor

        super(Communicator, self).__init__(acceptor.client, socket)

    def close(self):
        items = []
        while not self.channel.empty():
            items.append(self.channel.get())
        print('{} closed. In channel: {}'.format(type(self).__name__,
                                                 natural_join('and', map(repr, items))))
        for item in items:
            self.channel.put_nowait(item)

        super(Communicator, self).close()

    def __str__(self):
        return '{}:{}'.format(super(Communicator, self).__str__(), self.target)

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
    def receive(self, timeout):
        """Receive the next transmission from target. Thread-safe.

        :return Request|Response:
        """
        return self._non_worker_thread_channel().get(True, timeout)

    def handle(self):
        try:
            while True:
                receiving = self._read()
                if receiving is None:
                    break
                print('{} put {}'.format(self, receiving))
                self.channel.put_nowait(receiving)
        except Exception as e:
            print('{} put {}'.format(self, e))
            self.channel.put_nowait(e)
