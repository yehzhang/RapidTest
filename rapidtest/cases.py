from copy import deepcopy
from inspect import getmembers, ismethod

from .user_interfaces import inject_dependency, user_mode, get_dependency
from .utils import is_iterable, identity

_sentinel = object()


class Case(object):
    """Contains a set of basic information needed to test the target.

    :param args: arguments passed to the target, or a sequence of operations, which consists of
        method names followed by arguments grouped in a list.
        If a method does not take arguments, it could be followed by nothing.
        Wherever a Collect object is placed in the operations, the value returned by the method
        preceding it will be collected in the result. If no Collect was specified, the value
        returned by the last method is collected.
        TODO Collect could not be placed at the beginning
    :param type target: TODO support other languages
    :param bool operation: whether the args are arguments or operations. Default to False
    :param function post_proc: a post-processing function that takes an output of a solution and
        transforms to another, or a list of such functions to be applied from left to right
    :param any result: intended output of a solution given args, or a target that produces the
        intended output
    :param bool|int|[int] in_place: whether output is in-place modified arguments or returned
        value. If in_place is an integer or a list of integers, only arguments on the corresponding
        indices are gathered.
    """

    current_test = None

    BIND_TARGET_CLASS = 'target'
    BIND_POST_PROCESSING = 'post_proc'
    BIND_RESULT = 'result'
    BIND_IN_PLACE = 'in_place'
    BIND_OPERATION = 'operation'
    BIND_KEYS = frozenset(
        [BIND_TARGET_CLASS, BIND_POST_PROCESSING, BIND_RESULT, BIND_IN_PLACE, BIND_OPERATION])

    _injected_targets = set()

    PRIMITIVE_TYPES = (int, float, bool, str) + tuple(
        filter(lambda x: isinstance(x, type), get_dependency().values()))

    def __init__(self, *args, **kwargs):
        self.initialized = False

        self.target_result = _sentinel
        self.target_name = None

        self.args = self.process_args(*args, **kwargs)
        self.params = self.process_params(**kwargs)

        if self.current_test:
            self.current_test.add_case(self)

    @classmethod
    def process_args(cls, *args, **kwargs):
        if kwargs.get('operation'):
            pass
        else:
            return args

    @classmethod
    def process_params(cls, **kwargs):
        invalid_kwargs = set(kwargs) - cls.BIND_KEYS
        if invalid_kwargs:
            invalid_kwargs = ', '.join(map(repr, invalid_kwargs))
            raise TypeError('Test parameters do not take {}'.format(invalid_kwargs))
        return {k: getattr(cls, 'process_' + k, identity)(v) for k, v in kwargs.items()}

    @classmethod
    def process_target(cls, target):
        # TODO support for function targets
        if not isinstance(target, type):
            raise TypeError('target is not a class')

        # Inject dependencies such as TreeNode into user's solutions
        if target not in cls._injected_targets:
            inject_dependency(target)
            cls._injected_targets.add(target)

        return target

    @classmethod
    def process_post_proc(cls, post_proc):
        if callable(post_proc):
            post_proc = [post_proc]
        elif is_iterable(post_proc):
            post_proc = list(post_proc)
            if not all(map(callable, post_proc)):
                raise TypeError('some post-processing is not callable')
        else:
            raise TypeError('post_proc is not of type callable or iterable')

        def _reduce_post_proc(x):
            for f in post_proc:
                x = f(x)
            return x

        return _reduce_post_proc

    @classmethod
    def process_in_place(cls, in_place):
        def _safe_get(args, i):
            if not (0 <= i < len(args)):
                raise ValueError('in_place is out of range')
            return args[i]

        if isinstance(in_place, bool):
            if in_place:
                return lambda args: args[0] if len(args) == 1 else args
        elif isinstance(in_place, int):
            return lambda args: _safe_get(args, in_place)
        elif is_iterable(in_place):
            in_place = list(in_place)
            if not all(isinstance(i, int) for i in in_place):
                raise TypeError('in_place is not an iterable of integers')
            return lambda args: [_safe_get(args, i) for i in in_place]
        else:
            raise TypeError('in_place is not of type bool, int or iterable')

    def _initialize(self, default_params=None):
        """Initialize parameters of this case.

        :param dict default_params: already processed test parameters, overridden by parameters
            passed in constructor
        """
        params = {} if default_params is None else dict(default_params)
        params.update(self.params)
        self.params = params

        target = self.params.get(self.BIND_TARGET_CLASS, None)
        if target is None:
            raise RuntimeError('target was not specified in Test nor Case')
        o = target()
        self.target_name, self.target_method = self.get_method(o)

        self.post_proc = self.params.get(self.BIND_POST_PROCESSING, identity)

        self.in_place_selector = self.params.get(self.BIND_IN_PLACE, None)

        result = self.params.get(self.BIND_RESULT, _sentinel)
        if result is _sentinel:
            raise RuntimeError('result was not specified')
        if callable(result):
            self.asserted_result = self._call(result, self.args)
        else:
            self.asserted_result = self.normalize_output(result)

        self.initialized = True

    def run(self):
        if self.target_result is _sentinel:
            # Not run yet
            if not self.initialized:
                self._initialize()
            self.target_result = self._call(self.target_method, self.args)
        return self.target_result == self.asserted_result

    def __str__(self):
        repr_args = ', '.join(map(repr, self.args))
        if self.target_result is not _sentinel:
            op_eq = '==' if self.target_result == self.asserted_result else '!='
            comp_res = '{} {} {}'.format(repr(self.target_result), op_eq,
                                         repr(self.asserted_result))
        else:
            comp_res = '?'
        return '{}({}) -> {}'.format(self.target_name, repr_args, comp_res)

    def _call(self, f, args):
        args = deepcopy(args)
        with user_mode('Calling this method is not supported when judging'):
            output = f(*args)
        if self.in_place_selector:
            output = self.in_place_selector(args)
        return self.normalize_output(output)

    def normalize_output(self, output):
        return self.post_proc(self._normalize_type(output))

    @classmethod
    def _normalize_type(cls, output):
        if isinstance(output, cls.PRIMITIVE_TYPES) or output is None:
            pass
        elif is_iterable(output):
            output = [cls._normalize_type(o) for o in output]
        else:
            raise RuntimeError('Type of output {} is invalid'.format(type(output)))
        return output

    @staticmethod
    def get_method(obj, name=None):
        if name:
            method = getattr(obj, name)
        else:
            methods = getmembers(obj, predicate=ismethod)
            methods = [(name, method) for name, method in methods if not name.startswith('_')]
            if len(methods) != 1:
                raise RuntimeError(
                    'Cannot find the target method. You may specify a list of operations to '
                    'execute as arguments to Case, or prepend all names of private methods with '
                    'underscores.')  # TODO
            [method] = methods
        return method


def runnable(f):
    class Runnable(object):
        def run(self, *args, **kwargs):
            return f(*args, **kwargs)

    return Runnable

# class Executor(object):
#     def __init__(self, target, ):
