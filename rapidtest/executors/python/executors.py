from copy import deepcopy
from inspect import isclass, getmodule, getmembers, ismethod

from .dependencies import get_dependencies
from ..common import BaseExecutor, ExecutionOutput, OperationOutput


class NativeExecutor(BaseExecutor):
    PRIMITIVE_TYPES = BaseExecutor.PRIMITIVE_TYPES + tuple(
        v for v in get_dependencies().values() if isclass(v))

    _injected_targets = set()

    def __init__(self, target, **kwargs):
        super(NativeExecutor, self).__init__(**kwargs)

        self.target = target
        self.inject_dependencies(target)

    def execute(self, operations):
        # Lazy-executing operations
        return ExecutionOutput(self._execute(*t) for t in self._get_tasks(operations))

    def _execute(self, func, op):
        """
        :return OperationOutput:
        """
        args = deepcopy(op.args)
        val = func(*args)
        if op.collect:
            if self.in_place_selector:
                val = self.in_place_selector(args)
            val = self.normalize_raw_output(val)
        else:
            val = None
        return OperationOutput(op.name, op.args, op.collect, val)

    def _get_tasks(self, operations):
        """
        :param Operations operations:
        :return [(callable, Operation)]:
        """
        raise NotImplementedError

    @classmethod
    def inject_dependencies(cls, target):
        """Inject dependencies such as TreeNode into user's solutions so that they can be used
        without importing. """
        if target in cls._injected_targets:
            return

        module = getmodule(target)
        if module is not None:
            dependency = get_dependencies()
            for obj_name, obj in dependency.items():
                if not hasattr(module, obj_name):
                    setattr(module, obj_name, obj)

        cls._injected_targets.add(target)


class ClassExecutor(NativeExecutor):
    def __init__(self, *args, **kwargs):
        super(ClassExecutor, self).__init__(*args, **kwargs)

        if not isclass(self.target):
            raise TypeError('Target is not a class')

    def _get_tasks(self, operations):
        # Extract methods to call
        tasks = []

        target_instance = self.target(*operations.init_args)
        for op in operations:
            op.name, func = self.get_target_method(target_instance, op.name)
            tasks.append((func, op))

        return tasks

    @classmethod
    def get_target_method(cls, target_instance, name=None):
        """Get from `target_instance` a method and its name.

        :param object target_instance:
        :param str name: ignored if target is Runnable. If not specified and target is not Runnable,
            return the only public method, if any.
        :return str, callable:
        """
        if name:
            func = getattr(target_instance, name)
            if not callable(func):
                raise RuntimeError("{} object's attribute {} is not callable".format(
                    repr(type(target_instance).__name__), repr(name)))
            method = name, func
        else:
            # Get a public method
            methods = getmembers(target_instance, predicate=ismethod)
            methods = [(name, f) for name, f in methods if not name.startswith('_')]
            if len(methods) != 1:
                raise RuntimeError(
                    'Cannot find the target method. You may specify operations as arguments to '
                    'Case if there are multiple methods to be called, or prepend all '
                    'names of private methods with underscores.')
            [method] = methods
        return method


class FunctionExecutor(NativeExecutor):
    def __init__(self, *args, **kwargs):
        super(FunctionExecutor, self).__init__(*args, **kwargs)

        if not callable(self.target):
            raise TypeError('Target is not a function')

    def _get_tasks(self, operations):
        if operations.init_args:
            raise ValueError('Target cannot be instantiated')

        func_name = self.target.__name__
        for op in operations:
            if op.name:
                if op.name != func_name:
                    raise ValueError(
                        'Operations contain a method name other than {}'.format(repr(func_name)))
            else:
                op.name = func_name

        return [(self.target, op) for op in operations]
