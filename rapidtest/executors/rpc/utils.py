from collections import defaultdict
from threading import Condition

from ...utils import Dictable


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


class queuedict(object):
    """queue.Queue-like dict implementation.

    queuedict.get(timeout) amounts to Queue.get(True, timeout). If waiter timed out or key does
    not exist, a KeyError is raised. Note that it is possible to trigger a KeyError if a key is
    set but deleted before get.
    queuedict[] amounts to Queue.get_nowait().

    queuedict[] = amounts to Queue.put_nowait().

    queuedict.pop amounts to Queue.get_nowait() and then removing key. It waits until all
    getting threads pass. If a key is popped multiple times before set again, a KeyError is
    raised.
    del queuedict[] raises a RuntimeError if there are waiters.

    All methods do not support the paradigm of using default value.
    """

    def __init__(self, lock):
        self.d = dict()
        self.mutex = lock
        self.waiter_conditions = defaultdict(lambda: Condition(lock))
        self.waiter_counts = defaultdict(int)

    def __setitem__(self, key, val):
        with self.mutex:
            if key in self.waiter_conditions:
                self.waiter_conditions[key].notify()
            self.d[key] = val

    def __getitem__(self, key):
        with self.mutex:
            return self.d[key]

    def get(self, key, timeout=None):
        with self.mutex:
            if key not in self:
                self.waiter_counts[key] += 1
                cond = self.waiter_conditions[key]
                cond.wait(timeout)
                cond.notify()
                self.waiter_counts[key] -= 1
            return self.d[key]

    def __delitem__(self, key):
        with self.mutex:
            if key in self.waiter_conditions:
                raise RuntimeError('there are other threads trying to get')
            del self.d[key]

    def pop(self, key):
        with self.mutex:
            cond = self.waiter_conditions[key]
            while key in self.waiter_counts:
                count = self.waiter_counts[key]
                if count == 0:
                    cond.notify_all()  # let all later getters and deleters face KeyError
                    break
                else:
                    cond.wait()
            del self.d[key]
            del self.waiter_conditions[key], self.waiter_counts[key]

    def __repr__(self):
        with self.mutex:
            return repr(self.d)

    def __str__(self):
        with self.mutex:
            return str(self.d)
