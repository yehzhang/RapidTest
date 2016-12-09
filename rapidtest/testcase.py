from __future__ import print_function
from copy import deepcopy
from functools import reduce
from inspect import getmembers, ismethod
from sys import stdout

from .utils import super_len, is_iterable, identity
from .user_interfaces import inject_dependency, user_mode, get_dependency

_sentinel = object()


class Case:
    """Contains a set of basic information needed to test the target.

    :param args: arguments passed to the target, or a sequence of operations, which consists of
        method names followed by arguments grouped in a list.
        If a method does not take arguments, it could be followed by nothing.
        Wherever a Collect object is placed in the operations, the value returned by the method
        preceding it will be collected in the result. If no Collect was specified, the value
        returned by the last method is collected.
        TODO Collect could not be placed at the beginning
    :param class target: TODO
    :param bool operation: whether the args are arguments or operations. Default to False
    :param function post_proc: a post-processing function or a list of such functions
    :param result:
    :param in_place: TODO
    """

    current_test = None

    BIND_TARGET_CLASS = 'target'
    BIND_POST_PROCESSING = 'post_proc'
    BIND_RESULT = 'result'
    BIND_IN_PLACE = 'in_place'
    BIND_KEYS = frozenset([BIND_TARGET_CLASS, BIND_POST_PROCESSING, BIND_RESULT, BIND_IN_PLACE])

    INJECTED_TARGETS = set()

    PRIMITIVE_TYPES = tuple([int, float, bool, str] + get_dependency())

    def __init__(self, *args, **kwargs):
        self.args = args
        self.initialized = False

        self.target_result = _sentinel
        self.target_name = None

        self.params = self.process_params(**kwargs)

        if self.current_test:
            self.current_test.add_case(self)

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
        if target not in cls.INJECTED_TARGETS:
            inject_dependency(target)
            cls.INJECTED_TARGETS.add(target)

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
            raise TypeError('post_proc is not a function or an iterable of functions')
        return reduce(lambda x, y: lambda z: y(x(z)), post_proc)

    @classmethod
    def process_in_place(cls, in_place):
        def _safe_get(args, i):
            if not (0 <= i < len(args)):
                raise ValueError('in_place is out of range')
            return args[i]

        if is_iterable(in_place):
            in_place = list(in_place)
            if not all(isinstance(i, int) for i in in_place):
                raise TypeError('in_place is not an iterable of integers')
            return lambda args: [_safe_get(args, i) for i in in_place]
        elif isinstance(in_place, bool):
            if in_place:
                return lambda args: args[0] if len(args) == 1 else args
        elif isinstance(in_place, int):
            return lambda args: _safe_get(args, in_place)
        else:
            raise ValueError('Type of in_place {} is invalid'.format(type(in_place)))

    def initialize(self, default_params=None):
        """Initialize parameters of this case.
        This method is called in Test. No need to call again.

        :param dict default_params: already processed test parameters
        """
        params = self.params
        self.params = {} if default_params is None else dict(default_params)
        self.params.update(params)

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
            result = self.execute(result)
        self.asserted_result = self.normalize_output(result)

        self.initialized = True

    def run(self):
        if self.target_result is _sentinel:
            # Not run yet
            if not self.initialized:
                self.initialize()
            output = self.execute(self.target_method)
            self.target_result = self.normalize_output(output)
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

    def execute(self, f):
        args = deepcopy(self.args)
        with user_mode('Calling this method is not supported when judging'):
            output = f(*args)
        if self.in_place_selector:
            output = self.in_place_selector(args)
        return output

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


class Test:
    """Manage cases, run them, and print results.

    :param type target: same as the keyword argument 'target' of the Case class
    :param kwargs: same as those of the Case class
    """

    def __init__(self, target=None, **kwargs):
        self._pending_sessions = [[]]
        self.passed_cases = []
        self.failed_cases = []

        self.closed = False

        if target is not None:
            kwargs[Case.BIND_TARGET_CLASS] = target
        self.bound_params = Case.process_params(**kwargs)

    def __del__(self):
        self.close()

    def __enter__(self):
        if Case.current_test:
            raise RuntimeError('There is already a test running')
        Case.current_test = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Case.current_test = None
        self._run_sessions()
        self.close()

    def __call__(self, *args, **kwargs):
        """Call self.add_generator() on behalf of user.
        Should be used as a decorator.

        :param kwargs: keyword arguments passed to add_generator()
        """
        # type_err_msg = (
        #     'Test object is a shortcut for calling add_generator if used as a decorator. The '
        #     'test-generating function decorated will be passed to add_generator when @t is used, '
        #     'or passed preceding other arguments when @t(*args, **kwargs) is used. '
        #     'Check the method signature of add_generator to see what arguments are taken. ')

        if len(args) == 1 and callable(args[0]) and not kwargs:
            # Used like @self
            [f] = args
            self.add_generator(f)
            return f

        else:
            # Used like @self(100), @self(repeat=100), etc
            def _d(f):
                self.add_generator(f, *args, **kwargs)
                return f

            return _d

    def add_generator(self, generator, repeat=100):
        """
        :param generator: a test-generating function that takes an index and returns a case
        :param int repeat: how many times to run the test-generating function, if provided
        """
        if not callable(generator):
            raise TypeError('generator is not a function')
        if not isinstance(repeat, int):
            raise TypeError('repeat is not an integer')
        if repeat > 0:
            self.separate()
            self._add_generator(generator(i) for i in range(repeat))

    def add_case(self, case):
        """Add a case to be run when run() is called next time."""
        self._initialize(case)
        self._pending_sessions[-1].append(case)

    def add_cases(self, cases):
        if isinstance(cases, (list, tuple)):
            # not a generator. Do not lazy-evaluate for validating params
            for case in cases:
                self.add_case(case)
        elif is_iterable(cases):
            # probably a generator, using lazy-evaluation
            self._add_generator(cases)
        else:
            raise TypeError('cases are not callable nor iterable')

    def _add_generator(self, gen):
        """Add a iterable of cases which are lazy-evaluated."""
        self._pending_sessions.append(self._initialize(case) for case in gen)

    def separate(self):
        if self._pending_sessions[-1]:
            self._pending_sessions.append([])

    def _initialize(self, case):
        """Called to initialize a case."""
        if not isinstance(case, Case):
            raise TypeError('case is not of type Case')
        case.initialize(self.bound_params)
        return case

    def run(self):
        """Run all pending cases."""
        self._run_sessions()

    def _run_sessions(self):
        """Cases are already initialized at this time."""
        if self.failed_cases:
            return

        exc = None

        i = 0
        for i, session in enumerate(self._pending_sessions, 1):
            iter_session = iter(session)
            passed_cases, failed_cases, exc = self._run_cases(iter_session)

            self.passed_cases.extend(passed_cases)
            if failed_cases:
                self.failed_cases.extend(failed_cases)
                self._pending_sessions.append(iter_session)
                break

        del self._pending_sessions[:i]
        self.closed = False

        if exc is not None:
            raise exc

    @staticmethod
    def _run_cases(cases):
        passed_cases = []
        failed_cases = []
        exc = None

        for c in cases:
            try:
                success = c.run()
            except Exception as e:
                exc = e
                success = False

            symbol = '.' if success else 'x'
            print(symbol, end='')
            stdout.flush()
            if success:
                passed_cases.append(c)
            else:
                failed_cases.append(c)
                break

        if passed_cases or failed_cases:
            print()
            stdout.flush()

        return passed_cases, failed_cases, exc

    def close(self):
        if not self.closed:
            self.print_stats()
            self.closed = True

    def print_stats(self):
        cnt_pending_cases = sum(map(super_len, self._pending_sessions))
        if self.failed_cases:
            print('Failed: {}'.format(self.failed_cases[0]))
        elif self.passed_cases:
            if not cnt_pending_cases:
                print('Passed all {} test cases'.format(len(self.passed_cases)))
        else:
            print('No case was tested')
        if cnt_pending_cases:
            print('Leaving {} pending cases'.format(cnt_pending_cases))
        stdout.flush()
