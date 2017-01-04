from collections import defaultdict
from threading import Condition, Lock

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

    queuedict[] = amounts to Queue.put_nowait().

    queuedict.get(key, block, timeout) amounts to Queue.get(block, timeout). If waiter timed out
    or key does not exist, a KeyError is raised. Note that it is possible to trigger a KeyError
    if a key is set but deleted before get.

    queuedict.pop(key, block) amounts to Queue.get(block) and then removing key. If a key is
    popped multiple times before set again, a KeyError is raised. If block is True, it waits
    until all getting threads pass. Otherwise it does not wait, and raises a RuntimeError if
    there are waiters.
    """

    def __init__(self):
        self.d = dict()
        l = self.mutex = Lock()
        self.waiters = defaultdict(lambda: [Condition(l), 0])

    def __setitem__(self, key, val):
        with self.mutex:
            if key in self.waiters:
                cond, _ = self.waiters[key]
                cond.notify()

            self.d[key] = val

    def get(self, key, block=True, timeout=None):
        with self.mutex:
            if block:
                if key not in self:
                    cond, cnt = self.waiters[key]
                    self.waiters[key][1] = cnt + 1
                    cond.wait(timeout)
                    cond.notify()
                    self.waiters[key][1] -= 1

            return self.d[key]

    def pop(self, key, block=True):  # TODO add timeout
        with self.mutex:
            if block:
                while key in self.waiters:
                    cond, cnt = self.waiters[key]
                    if cnt == 0:
                        cond.notify_all()  # let all later getters and deleters face KeyError
                        del self.waiters[key]
                        break
                    else:
                        cond.wait()
            else:
                if key in self.waiters:
                    raise RuntimeError('there are other threads trying to get')

            return self.d.pop(key)

    def __repr__(self):
        with self.mutex:
            return repr(self.d)

    def __str__(self):
        with self.mutex:
            return str(self.d)

    def __iter__(self):
        return iter(self.d)
