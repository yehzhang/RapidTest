import atexit
import logging
from inspect import isclass

from .common_executors import BaseExecutor
from .externel_executors import ExternalExecutorFabric
from .java import *
from .operations import Operation, Operations
from .python import *
from ..utils import isstring

logger = logging.getLogger(__name__)


class BaseTarget(object):
    def __init__(self, executor):
        self.executor = executor


class Target(BaseTarget):
    _executors_pool = {}

    def __init__(self, target, target_name=None, env=None):
        """Factory class for building executors

        :param Callable|str target: a native object or a path to an external file, which contains
            the structure to be tested
        :param str target_name: if target is a path, this indicates the name of the structure to
            test
        :param str env: environment of the target, usually just the language name itself
        """
        executor_id = (target, target_name)
        if executor_id not in self._executors_pool:
            # Find the corresponding executor
            if isstring(target):
                cls = ExternalExecutorFabric.get(env) or ExternalExecutorFabric.guess(target)
                executor = cls(target, target_name)

            elif callable(target):
                executor = (ClassExecutor if isclass(target) else FunctionExecutor)(target)

            else:
                raise TypeError('Target is not a callable nor str')

            self._executors_pool[executor_id] = executor

        super(Target, self).__init__(self._executors_pool[executor_id])

    @classmethod
    def close(cls):
        for executor_id, e in list(cls._executors_pool.items()):
            target, _ = executor_id
            logger.debug('Executor %s on %s closed', e.ENVIRONMENT, target)
            e.close()
            del cls._executors_pool[executor_id]


def _close_executors():
    Target.close()


atexit.register(_close_executors)
del _close_executors
