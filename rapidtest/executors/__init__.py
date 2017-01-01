from inspect import isclass

from .common_executors import BaseExecutor, ExternalExecutorFabric
from .operations import Operation, Operations
from .java import *
from .python import *
from ..utils import isstring


class Target(object):
    _cache = {}

    def __init__(self, target, target_name=None, env=None):
        """Factory class for building executors

        :param callable|str target: a native object or a path to an external file, which contains
            the structure to be tested
        :param str target_name: if target is a path, this indicates the name of the structure to
            test
        :param str env: environment of the target, usually just the language name itself
        """
        executor_id = (target, target_name)
        if executor_id not in self._cache:
            # Find the corresponding executor
            if isstring(target):
                cls = ExternalExecutorFabric.get(env) or ExternalExecutorFabric.guess(target)
                executor = cls(target, target_name)

            elif callable(target):
                executor = (ClassExecutor if isclass(target) else FunctionExecutor)(target)

            else:
                raise TypeError('Target is not a callable nor str')

            self._cache[executor_id] = executor

        self.executor = self._cache[executor_id]
