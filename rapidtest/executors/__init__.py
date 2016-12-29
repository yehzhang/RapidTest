from inspect import isclass

from .common import BaseExecutor, Operation, Operations
from .python import *


class Target(object):
    _cache = {}

    def __init__(self, target, lang=None, class_name=None):
        """
        :param callable|str target:
        :param str lang:
        :param str class_name:
        """
        exec_id = (target, class_name)
        if exec_id not in self._cache:
            # Find the corresponding executor
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
            self._cache[exec_id] = cls(target)

        self.executor = self._cache[exec_id]

    def complete(self, *args, **kwargs):
        self.executor.initialize(*args, **kwargs)
        return self.executor
