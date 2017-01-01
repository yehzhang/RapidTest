from copy import deepcopy
from inspect import isclass, getmembers, ismethod, getmodule

from .dependencies import get_dependencies
from ..common_executors import BaseExecutor
from ..outputs import OperationOutput


class NativeExecutor(BaseExecutor):
    PRIMITIVE_TYPES = BaseExecutor.PRIMITIVE_TYPES + tuple(
        v for v in get_dependencies().values() if isclass(v))

    _injected_targets = set()

    def __init__(self, target):
        super(NativeExecutor, self).__init__(target)

        self.inject_dependencies(target)

    def _execute(self, operations):
        funcs = self.get_functions(operations)
        # Lazy-evaluate operations
        return (self._execute_operation(*t) for t in zip(funcs, operations))

    def _execute_operation(self, func, op):
        args = deepcopy(op.args)
        val = func(*args)
        if self.in_place_selector:
            val = self.in_place_selector(args)
        val = self.normalize_raw_output(val)
        return OperationOutput(op.name, op.args, op.collect, val)

    def get_functions(self, operations):
        """
        :param Operations operations:
        :return [callable]:
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
    def __init__(self, target):
        super(ClassExecutor, self).__init__(target)

        if not isclass(target):
            raise TypeError('Target is not a class')

        self.target_instance = None
        self.default_method = None

    def get_functions(self, operations):
        # Extract methods to call
        funcs = []

        self.target_instance = self.target(*operations.init_args)
        for op in operations:
            op.name, func = self.get_method(op.name)
            funcs.append(func)

        return funcs

    def get_method(self, name=None):
        """Get from `self.target_instance` a method and its name.

        :param str name: If not specified, return the only public method, if any.
        :return str, callable:
        """
        if name:
            func = getattr(self.target_instance, name)
            if not callable(func):
                raise RuntimeError("{} object's attribute {} is not callable".format(
                    repr(type(self.target_instance).__name__), repr(name)))
            method = name, func
        else:
            # Get a public method
            if self.default_method is None:
                methods = getmembers(self.target_instance, predicate=ismethod)
                methods = [(name, f) for name, f in methods if not name.startswith('_')]
                if len(methods) != 1:
                    raise RuntimeError(
                        'Cannot find the target method. You may specify operations as arguments '
                        'to Case if there are multiple methods to be called, or prepend all names '
                        'of private methods with underscores.')
                [self.default_method] = methods
            method = self.default_method
        return method


class FunctionExecutor(NativeExecutor):
    def __init__(self, target):
        super(FunctionExecutor, self).__init__(target)

        if not callable(target):
            raise TypeError('Target is not a function')

    def get_functions(self, operations):
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

        return [self.target for _ in operations]
