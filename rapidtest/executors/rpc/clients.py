from json import JSONDecoder, JSONEncoder

from .exceptions import ExternalException, TimeoutError
from .utils import Request, Response
from .workers import Acceptor
from ..._compat import raise_from
from ...data_structures import get_dependencies


class ExecutionTargetRPCClient(object):
    _count_requests = 0

    METHOD_HELLO = 'hello'  # first server send to client a notification with target_id as params
    METHOD_EXECUTE = 'execute'
    METHOD_TERMINATE = 'terminate'
    WHO_I_AM = 'target'

    def __init__(self, addr):
        """
        :param Tuple[str, int] addr:
        """
        self.acceptor = None
        self.addr = addr

        # TODO move to executor?
        self.encoder = JSONEncoder(separators=(',', ':'), default=lambda x: x.as_json_object())

        dependencies = get_dependencies()
        dependencies.update({T.__name__: T for T in (ExternalException,)})
        self.decoder = JSONDecoder(object_hook=self._get_object_hook_handler(dependencies))

    def __del__(self):
        self.close()

    def run(self):
        """
        :return Tuple[str, int]: address of socket
        """
        if self.acceptor is None:
            self.acceptor = Acceptor(self)
            self.addr = self.acceptor.get_socket_address()
        return self.addr

    def close(self):
        if not self.closed():
            ator = self.acceptor
            ator.close()
            ator.join()
            self.acceptor = None
            ator.raise_()

    def closed(self):
        return self.acceptor is None

    def connect(self, target, timeout=None):
        """Wait until target is connected.

        :param Any target:
        :param int timeout: Wait for specified seconds before raising an exception
        """
        self.acceptor.get_workers(target, timeout)

    def request(self, target, method, params, receive_timeout=None):
        """Send request and wait for response.

        :param Any target:
        :param str method:
        :param List[Any] params:
        :return Response:
        :param int receive_timeout:
        """
        request_id = self.new_id()
        self._send(target, Request(method, params, request_id))
        return self._wait_response(target, request_id, receive_timeout)

    def notify(self, target, method, params=None):
        """Send notification and return immediately.

        :param Any target:
        :param str method:
        :param List[Any] params:
        """
        request = Request(method, params)
        self._send(target, request)

    def disconnect(self, target):
        self.acceptor.remove_workers(target)

    def _send(self, target, call):
        """Send call to target.

        :param Call call:
        """
        _, s = self.acceptor.get_workers(target)
        s.send(call)

    def _wait_response(self, target, id, timeout):
        """
        :param Any id: None means notification
        :return Any: result of a response or exception
        """
        r, _ = self.acceptor.get_workers(target)
        try:
            call = r.receive(id, timeout)
        except TimeoutError:
            # TODO send timeout to target so that I can tell IOError from TLE. Or is that important?
            raise

        assert call.id == id
        if isinstance(call, Response):
            if call.error:
                exc, ext_exc = call.error.to_exceptions()
                raise_from(exc, ext_exc)
            else:
                return call.result
        else:
            raise RuntimeError('target did not return a Response')

    @classmethod
    def _get_object_hook_handler(cls, dependencies):
        """Python object from external sources must be instantiated with constructor. """

        def _object_hook_handler(d):
            ctor_pair = d.pop('__jsonclass__', None)
            if ctor_pair is not None:
                ctor_name, params = ctor_pair
                if ctor_name not in dependencies:
                    raise NameError('name {} is not defined'.format(repr(ctor_name)))
                T = dependencies[ctor_name]
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
