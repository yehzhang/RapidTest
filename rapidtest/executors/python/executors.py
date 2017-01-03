from copy import deepcopy
from inspect import isclass, getmembers, ismethod, getmodule

from ..exceptions import MSG_CANNOT_GUESS_METHOD
from ..dependencies import get_dependencies
from ..common_executors import BaseExecutor


class NativeExecutor(BaseExecutor):
    PRIMITIVE_TYPES = BaseExecutor.PRIMITIVE_TYPES + tuple(
        v for v in get_dependencies().values() if isclass(v))

    _injected_targets = set()

    def __init__(self, target):
        super(NativeExecutor, self).__init__(target)

        self.inject_dependencies(target)

    def execute_operations(self, operations):
        """Lazy-evaluate operations but get functions immediately. """
        return (self._execute(*t) for t in zip(self.get_functions(operations), operations))

    def _execute(self, func, op):
        args = deepcopy(op.args)
        val = func(*args)
        if self.in_place_selector:
            val = args
        return self.finalize_operation(op, val)

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
            raise TypeError('target is not a class')

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
                    raise RuntimeError(MSG_CANNOT_GUESS_METHOD)
                [self.default_method] = methods
            method = self.default_method
        return method


class FunctionExecutor(NativeExecutor):
    def __init__(self, target):
        super(FunctionExecutor, self).__init__(target)

        if not callable(target):
            raise TypeError('target is not a function')

    def get_functions(self, operations):
        if operations.init_args:
            raise ValueError('target cannot be instantiated')

        func_name = self.target.__name__
        for op in operations:
            if op.name:
                if op.name != func_name:
                    raise ValueError(
                        'operations contain a method name other than {}'.format(repr(func_name)))
            else:
                op.name = func_name

        return [self.target for _ in operations]
