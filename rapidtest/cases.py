from .executors import Executor
from .utils import is_iterable, identity, sentinel


class Case(object):
    """Contains a set of basic information needed to test the target.

    :param args: see `Executor.process_args()`
    :param callable|type target: a function that produces output when called with args or a class
        that produces output.
        # TODO support other languages
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

    def __init__(self, *args, **kwargs):
        self.initialized = False

        self.args = args
        self.executor = Executor(args, kwargs.get(self.BIND_OPERATION, False))
        self.target_result = None

        self.params = self.process_params(**kwargs)

        if self.current_test:
            self.current_test.add_case(self)

    def __str__(self):
        return 'Case is not run yet' if self.target_result is None else str(self.target_result)

    @classmethod
    def process_params(cls, **kwargs):
        invalid_kwargs = set(kwargs) - cls.BIND_KEYS
        if invalid_kwargs:
            invalid_kwargs = ', '.join(map(repr, invalid_kwargs))
            raise TypeError('Test parameters do not take {}'.format(invalid_kwargs))
        return {k: getattr(cls, 'process_' + k, identity)(v) for k, v in kwargs.items()}

    @classmethod
    def process_post_proc(cls, post_proc):
        if callable(post_proc):
            post_proc = [post_proc]
        elif is_iterable(post_proc):
            post_proc = list(post_proc)
            if not all(map(callable, post_proc)):
                raise TypeError('Some post-processing is not callable')
        else:
            raise TypeError('Post_proc is not of type callable or iterable')

        def _reduce_post_proc(x):
            for f in post_proc:
                x = f(x)
            return x

        return _reduce_post_proc

    @classmethod
    def process_in_place(cls, in_place):
        def _safe_get(args, i):
            if not (0 <= i < len(args)):
                raise ValueError('In_place is out of range')
            return args[i]

        if isinstance(in_place, bool):
            if in_place:
                return lambda args: args[0] if len(args) == 1 else args
        elif isinstance(in_place, int):
            return lambda args: _safe_get(args, in_place)
        elif is_iterable(in_place):
            in_place = list(in_place)
            if not all(isinstance(i, int) for i in in_place):
                raise TypeError('In_place is not an iterable of integers')
            return lambda args: [_safe_get(args, i) for i in in_place]
        else:
            raise TypeError('In_place is not of type bool, int or iterable')

    def _initialize(self, default_params=None):
        """Initialize parameters of this case.

        :param dict default_params: already processed test parameters, overridden by parameters
            passed in constructor
        """
        if self.initialized:
            return

        params = {} if default_params is None else dict(default_params)
        params.update(self.params)
        self.params = params

        target = self.params.get(self.BIND_TARGET_CLASS, None)
        if target is None:
            raise RuntimeError('Target was not specified in Test nor Case')
        post_proc = self.params.get(self.BIND_POST_PROCESSING)
        in_place_selector = self.params.get(self.BIND_IN_PLACE)
        self.executor.initialize(target, post_proc, in_place_selector)

        result = self.params.get(self.BIND_RESULT, sentinel)
        if result is sentinel:
            raise RuntimeError('Result was not specified')
        if callable(result):
            self.asserted_vals = self.executor.run(result)
        else:
            self.asserted_vals = self.executor.normalize_raw_output(result)

        self.initialized = True

    def run(self):
        if self.target_result is None:
            self._initialize()
            self.target_result = self.executor.run()
        return self.target_result.check(self.asserted_vals)
