from inspect import isclass

from .common import BaseExecutor, Operation, Operations
from .python import *


def make_target(target, lang=None, class_name=None):
    """

    :param callable|str target:
    :param str lang:
    :param str class_name:
    :return ExecutorStub:
    """
    stub = _executor_stubs.get((target, class_name))
    if stub is None:

        if isinstance(target, str):
            # TODO
            pass
        elif callable(target):
            if isclass(target):
                cls = ClassExecutor
            else:
                cls = FunctionExecutor
        else:
            raise TypeError('Target is not a callable nor str')
        stub = ExecutorStub(cls, target)

        _executor_stubs[target] = stub
    return stub

_executor_stubs = {}


class ExecutorStub(object):
    def __init__(self, cls, *args, **kwargs):
        self.executor = cls(*args, **kwargs)

    def complete(self, *args, **kwargs):
        self.executor.initialize(*args, **kwargs)
        return self.executor
