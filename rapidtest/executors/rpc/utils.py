from collections import defaultdict
from threading import Lock, Condition


class JsonSerializable(object):
    def as_json_object(self):
        """A dict describing an object in the external executor with the format:
        {
            "__jsonclass__": ["constructor_name", [constructor_params, ...]],
            "attribute1": value1,
            "attribute2": value2,
            ...
        }

        The object can be instantiated using either constructor or attributes.
        If constructor is used, attributes are ignored.

        :return Dict:
        """
        init_params = self.as_constructor_params()
        if init_params is None:
            obj = self.as_attributes()
        else:
            obj = {}
        obj['__jsonclass__'] = [self.get_external_name(), init_params]
        return obj

    def get_external_name(self):
        """
        :return Tuple[str, str]: name of the external object to be instantiated,
            and the factory method to be called. None means calling constructor
        """
        return type(self).__name__, None

    def as_attributes(self):
        """
        :return Dict[str, Any]: values of dict should also be json-serializable
        """
        return dict((k, v) for k, v in self.__dict__.items() if v is not None)

    def as_constructor_params(self):
        """
        :return List:
        """
        return None


class ExternalObject(JsonSerializable):
    def __init__(self, target_name, init_args, constructor_name=None):
        self.target_name = target_name
        self.constructor_name = constructor_name
        self.init_args = init_args

    def as_constructor_params(self):
        return self.init_args

    def get_external_name(self):
        return self.target_name, self.constructor_name


class Call(JsonSerializable):
    def __init__(self, id):
        self.id = id


class Request(Call):
    """Request in JSON-RPC"""

    def __init__(self, method=None, params=None, id=None):
        super(Request, self).__init__(id)
        self.method = method
        self.params = params


class Response(Call):
    """Response in JSON-RPC"""

    def __init__(self, result=None, error=None, id=None):
        super(Response, self).__init__(id)
        self.result = result
        self.error = error


class queuedict(object):
    """queue.Queue-like dict implementation.

    queuedict[] = amounts to Queue.put_nowait().

    queuedict.pop(key, block, timeout) amounts to Queue.get(block, timeout). If waiter timed out
    or key does not exist, a KeyError is raised. Note that it is possible to trigger a KeyError
    if a key is set but popped before get.

    queuedict.get(key, block, timeout) amounts to queuedict.pop without removal. It is not safe
     to get and pop at the same time.
    """

    def __init__(self):
        self.d = dict()
        l = self.mutex = Lock()
        self.waiter_conditions = defaultdict(lambda: Condition(l))

    def __setitem__(self, key, val):
        with self.mutex:
            if key in self.waiter_conditions:
                self.waiter_conditions[key].notify()

            self.d[key] = val

    def get(self, key, block=True, timeout=None):
        with self.mutex:
            cond = self._wait_data(key, block, timeout)
            if cond:
                cond.notify()

            return self.d[key]

    def pop(self, key, block=True, timeout=None):
        with self.mutex:
            self._wait_data(key, block, timeout)

            del self.waiter_conditions[key]
            return self.d.pop(key)

    def _wait_data(self, key, block, timeout):
        if block:
            if key not in self.d:
                cond = self.waiter_conditions[key]
                cond.wait(timeout)
                return cond

    def __repr__(self):
        with self.mutex:
            return repr(self.d)

    def __str__(self):
        with self.mutex:
            return str(self.d)

    def __contains__(self, key):
        with self.mutex:
            return key in self.d

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        with self.mutex:
            return list(self.d.values())

    def keys(self):
        with self.mutex:
            return list(self.d.keys())

    def items(self):
        with self.mutex:
            return list(self.d.items())
