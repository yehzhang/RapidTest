from .executors import Operation, Operations, Target
from .utils import is_iterable, identity, natural_join, nop, is_sequence, sentinel, is_string, \
    Sentinel


class Case(object):
    """Contains a set of basic information required to test the target. All of the kwargs below
    could be specified in `Test` constructor.

    :param args: `args` has two formats: arguments or a sequence of operations.

        When the first format is used, args will be passed to `target`, and its returned value will
        be compared against `result`.

        When the second format is used, operations will be executed one by one.

        operations := operation, operations
        operation := method_name[, arguments][, result]

        method_name is name of the method in target to be called.

        arguments is a list of arguments to be passed to the method. If the method does not take
        arguments, this could be omitted.

        result is a `rapidtest.Result()` object specifying the asserted returned value from the
        method called. If an operation has no such object, the returned value is discarded.

    :param bool operation: whether args are of the second format or the first one. Default to
        use the first format.

    :param callable|Target target: a function or class to be tested. If it is a class and
        `operation` is False, the only public method will be called, if any.
        Alternatively target can be a value returned by make_target().
        # TODO support other languages

    :param callable|iterable post_proc: a post-processing function that takes a returned value and
        processes it, or an sequence of such functions to be applied from left to right.

        Note that post_proc will be applied to result, if it is a plain value.

    :param any result: if this parameter is a class or function, it will be treated as another
        `target`, with its output being compared.

        Otherwise, this parameter could only be used when `operation` is False, which means
        `result` is the asserted returned value of `target`.

    :param bool|int|[int] in_place: whether output should be in-place modified arguments or
        returned value. If in_place is an integer or a list of integers, only arguments on the
        corresponding indices are collected.
    """

    current_test = None

    BIND_EXECUTOR_STUB = 'target'
    BIND_POST_PROC_FUNCS = 'post_proc'
    BIND_RESULT = 'result'
    BIND_IN_PLACE_SELECTOR = 'in_place'
    BIND_IS_OPERATION = 'operation'
    BIND_KEYS = frozenset(
        [BIND_EXECUTOR_STUB, BIND_POST_PROC_FUNCS, BIND_RESULT, BIND_IN_PLACE_SELECTOR,
         BIND_IS_OPERATION])

    def __init__(self, *args, **kwargs):
        self.initialized = False

        self.args = args
        self.executor = None
        self.execution_output = None

        self.params = self.preprocess_params(**kwargs)

        if self.current_test:
            self.current_test.add_case(self)

    def __str__(self):
        return str(self.execution_output) if self.execution_output else 'Case is not run yet'

    @classmethod
    def preprocess_params(cls, **kwargs):
        invalid_kwargs = set(kwargs) - cls.BIND_KEYS
        if invalid_kwargs:
            repr_kws = natural_join('and', map(repr, invalid_kwargs))
            raise TypeError('Test parameters do not take {}'.format(repr_kws))
        return {k: getattr(cls, 'preprocess_' + k, identity)(v) for k, v in kwargs.items()}

    @classmethod
    def preprocess_target(cls, target):
        if not isinstance(target, Target):
            target = Target(target)
        return target

    @classmethod
    def preprocess_post_proc(cls, post_proc):
        if callable(post_proc):
            post_procs = [post_proc]
        elif is_iterable(post_proc):
            post_procs = list(post_proc)
            if not all(map(callable, post_procs)):
                raise TypeError('Some post-processing is not callable')
        else:
            raise TypeError('Post_proc is not of type callable or iterable')
        return post_procs

    @classmethod
    def preprocess_result(cls, result):
        if callable(result):
            # callable result is treated like target
            result = cls.preprocess_target(result)
        return result

    @classmethod
    def preprocess_in_place(cls, in_place):
        def _safe_get(args, i):
            if not (0 <= i < len(args)):
                raise ValueError('In_place is out of range')
            return args[i]

        if isinstance(in_place, bool):
            if in_place:
                return identity
        elif isinstance(in_place, int):
            return lambda args: _safe_get(args, in_place)
        elif is_iterable(in_place):
            in_place = list(in_place)
            if not all(isinstance(i, int) for i in in_place):
                raise TypeError('One element of in_place is not an integer')
            return lambda args: [_safe_get(args, i) for i in in_place]
        else:
            raise TypeError('In_place is not of type bool, int or iterable')

    @classmethod
    def process_args(cls, args, operation):
        """
        :return Operations:
        """
        if operation:
            init_args, ops = ArgsParser().parse(args)
        else:
            init_args = ()
            ops = [Operation(args=args, collect=True)]
        return Operations(init_args, ops)

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

        # Process post_proc and in_place
        post_proc_funcs = self.params.get(self.BIND_POST_PROC_FUNCS, [])

        selector = self.params.get(self.BIND_IN_PLACE_SELECTOR)
        if selector:
            post_proc_funcs = [selector] + post_proc_funcs
            in_place = True
        else:
            in_place = False

        if post_proc_funcs:
            def post_proc(x):
                for f in post_proc_funcs:
                    x = f(x)
                return x
        else:
            post_proc = None

        # Create executor
        stub = self.params.get(self.BIND_EXECUTOR_STUB)
        if stub is None:
            raise RuntimeError('Target was specified in neither Test nor Case')
        is_operation = self.params.get(self.BIND_IS_OPERATION, False)
        self.executor = stub.complete(post_proc=post_proc, in_place=in_place)

        # Process operation, result, and Result()
        self.operations = self.process_args(self.args, is_operation)
        bound_result = self.params.get(self.BIND_RESULT, sentinel)
        result_objects = [item for item in self.args if isinstance(item, Result)]
        if result_objects and bound_result is not sentinel:
            raise RuntimeError('Both Result() object and result= keyword is specified')
        if isinstance(bound_result, Target):
            # Result is another target
            result_executor = bound_result.complete(post_proc=post_proc, in_place=in_place)
            # At least collect something
            if not any(op.collect for op in self.operations):
                for op in self.operations:
                    op.collect = True
            vals = result_executor.execute(self.operations).get_val()
        else:
            if is_operation:
                # Used Result() objects.
                if bound_result is not sentinel:
                    raise RuntimeError(
                        'result= keyword can only be a target when operation is True. You may '
                        'want to use Result() object')
                if not result_objects:
                    raise RuntimeError('Result() object is not specified when operation is True')
                # Turn them into plain values
                result_vals = (r.val for r in result_objects)
            else:
                # Used a plain value
                if result_objects:
                    raise RuntimeError(
                        'Result() object is not accepted when operation is False. Please use '
                        'result= keyword')
                if bound_result is sentinel:
                    raise RuntimeError('result is not specified')
                result_vals = [bound_result]
            vals = [self.executor.normalize_raw_output(v) for v in result_vals]
        self.asserted_output_vals = vals

        self.initialized = True

    def run(self):
        if self.execution_output is None:
            self._initialize()
            self.execution_output = self.executor.execute(self.operations)
            self.execution_output.check(self.asserted_output_vals)
        return self.execution_output.result


class Result(Sentinel):
    pass


class ArgsParser(object):
    NAME = 'name'
    NEXT_NAME = 'next_name'
    INIT_ARGS = 'init_args'
    ARGS = 'args'
    RSLT = 'result'

    START_STATE = INIT_ARGS, NAME
    TRANS = {
        (INIT_ARGS, NAME):       ((NAME,), (NEXT_NAME, ARGS, RSLT), 'empty_args'),
        (NAME,):                 ((NEXT_NAME, ARGS, RSLT), ''),
        (NEXT_NAME, ARGS, RSLT): (
            (NEXT_NAME, ARGS, RSLT), (NEXT_NAME, RSLT), (NAME,), 'push_stub'),
        (NEXT_NAME, RSLT):       ((NEXT_NAME, ARGS, RSLT), (NAME,), 'push_stub'),
    }

    REPRS = {
        NAME:      'method name',
        NEXT_NAME: 'method name',
        INIT_ARGS: '__init__ arguments',
        ARGS:      'arguments',
        RSLT:      'result object',
    }

    def push_stub(self):
        self.operations.append(self.curr_operation)
        self.curr_operation = Operation()

    @classmethod
    def get_symbol(cls, item, state):
        if isinstance(item, Result):
            symbols = cls.RSLT,
        elif is_string(item):
            symbols = cls.NAME, cls.NEXT_NAME
        elif is_sequence(item):
            symbols = cls.INIT_ARGS, cls.ARGS
        else:
            symbols = []
        # assert at most one of symbols is in state
        for s in symbols:
            if s in state:
                return s

    def empty_args(self):
        raise ValueError('No args is specified')

    def handle_init_args(self):
        self.init_args = self.item

    def handle_next_name(self):
        self.push_stub()
        self.handle_name()

    def handle_name(self):
        self.curr_operation.name = self.item

    def handle_result(self):
        self.curr_operation.collect = True
        self.push_stub()

    def handle_args(self):
        self.curr_operation.args = self.item

    def parse(self, args):
        """
        :return (any, ...), [Operation]: the first returned value is arguments to be passed to
            the constructor of target
        """
        self.init_args = ()
        self.operations = []
        self.state = self.START_STATE
        self.curr_operation = Operation()

        for item in args:
            self.item = item

            symbol = self.get_symbol(item, self.state)
            if symbol is None:
                # symbol that is not accepted in current self.state
                expected = natural_join('or', map(self.REPRS.get, self.state))
                raise ValueError('expected {}, got {}'.format(expected, repr(item)))

            handler_name = 'handle_' + symbol
            getattr(self, handler_name)()

            next_states = self.TRANS[self.state]
            self.state = next_states[self.state.index(symbol)]

        end_handler_name = self.TRANS[self.state][-1]
        getattr(self, end_handler_name, nop)()

        if not self.operations:
            raise ValueError('Args contains no method call')

        ret = tuple(self.init_args), self.operations
        return ret
