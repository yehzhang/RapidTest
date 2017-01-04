import traceback
from select import select
from socket import socket
from threading import Thread

from .exceptions import TimeoutError
from .utils import Request, Response, queuedict, Call
from ..._compat import queue, raise_from


class ThreadedSocketWorker(object):
    _count_workers = 0

    def __init__(self, client, socket):
        self.id = self._count_workers
        ThreadedSocketWorker._count_workers += 1
        self.client = client
        self.socket = socket
        self.closed = False

        self._read_buf = ''

        self._working = False
        self.exception = None
        self.thread = self._start_thread()

    def __del__(self):
        self.close()

    def close(self):
        print('{} closed.'.format(type(self).__name__))
        self.socket.close()
        self.closed = True

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
            except OSError:
                print(
                    'Worker {} ends with OSError ignored: {}'.format(self, traceback.format_exc()))
                pass
            except BaseException as e:
                # Store exception raised in child thread
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

    def get_address(self):
        return self.socket.getsockname()

    def _ensure_working(self):
        if not self._working:
            raise RuntimeError('connection already closed')

    def _read(self, s=None):
        """
        :param socket s:
        :return Call:
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


class Acceptor(ThreadedSocketWorker):
    def __init__(self, client):
        s = socket()
        s.bind(client.addr)
        s.listen(5)

        super(Acceptor, self).__init__(client, s)

        self.workers = queuedict()

    def handle(self):
        while True:
            # Accept
            conn, _ = self.socket.accept()
            print('Python accept from: {}:{}'.format(*_))
            call = self._read(conn)
            if call is None:
                break
            if not isinstance(call, Request) or call.method != self.client.METHOD_HELLO:
                # Raise an exception for now
                raise RuntimeError('Initial request of a connection was invalid')

            target = call.params[0]
            workers = Receiver(self, target, conn), Sender(self, target, conn)
            print('Python created communicators: {}, {}'.format(*workers))
            self.workers[target] = workers

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

        print('Workers remaining: {}'.format(self.workers))
        for target in self.workers:
            self.remove_workers(target)

        super(Acceptor, self).close()

    # noinspection PyUnboundLocalVariable
    def get_workers(self, target, timeout=None):
        """
        :param Any target:
        :param int timeout:
        :return Tuple[Communicator, Communicator]: (receiver, sender)
        """
        try:
            return self.workers.get(target, True, timeout)
        except KeyError:
            raise_from(TimeoutError('target did not connect in time or is already removed'), None)

    # noinspection PyUnboundLocalVariable
    def remove_workers(self, target):
        """Remove workers to release memory. Client calls this method when no longer communications
            with target. """
        try:
            r, s = self.workers.pop(target, False)
        except RuntimeError:
            raise_from(RuntimeError('connection does not exist.'), None)

        r.close()
        s.close()
        r.join()
        s.join()


# noinspection PyAbstractClass
class Communicator(ThreadedSocketWorker):
    def __init__(self, acceptor, target, socket):
        self.target = target
        self.acceptor = acceptor

        super(Communicator, self).__init__(acceptor.client, socket)

    def __str__(self):
        return '{}:{}'.format(super(Communicator, self).__str__(), self.target)

    def _non_worker_thread_access(self):
        """Make sure exception is passed to the main thread and prevents deadlock."""
        self.raise_()
        self._ensure_working()


class Sender(Communicator):
    def __init__(self, acceptor, target, socket):
        self.channel = queue.Queue()

        super(Sender, self).__init__(acceptor, target, socket)

    # def close(self):
    #     print('{} closed. In channel: {}'.format(type(self).__name__, self.channel)
    #     super(Communicator, self).close()

    def send(self, call):
        """Send call to target. Thread-safe.

        :param Call call:
        """
        if not isinstance(call, Call):
            raise TypeError("'call' is not a Call")
        self._non_worker_thread_access()
        self.channel.put_nowait(call)

    def handle(self):
        while True:
            call = self.channel.get(True)
            if call is None:
                break
            self._send(call)

    def close(self):
        self.channel.put_nowait(None)  # None means terminating
        super(Communicator, self).close()

    def _send(self, call):
        """
        :param Call call:
        """
        data = self.client.encoder.encode(dict(call))
        self.socket.send('{} '.format(len(data)).encode())
        self.socket.send(data.encode())
        print('Python send: ' + data)


class Receiver(Communicator):
    def __init__(self, acceptor, target, socket):
        super(Receiver, self).__init__(acceptor, target, socket)

        self.channels = queuedict()

    def receive(self, id, timeout):
        """Receive the next transmission from target. Thread-safe.

        :return Call:
        """
        self._non_worker_thread_access()
        try:
            return self.channels.get(id, True, timeout)
        except KeyError:
            raise_from(TimeoutError('target did not respond in time'), None)
            # technically speaking did not respond with the corresponding id

    def handle(self):
        while True:
            call = self._read()
            if call is None:
                break
            print('{} put {}'.format(self, call))
            self.channels[call.id] = call
