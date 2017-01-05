from collections import defaultdict
from threading import Lock, Condition

from ...utils import Dictable


class Call(Dictable):
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
