from copy import deepcopy
from inspect import getmembers, ismethod

from .user_interface import inject_dependency, user_mode, get_dependency
from .utils import is_iterable, identity, OneTimeSetProperty, Sentinel, natural_join, nop, \
    sentinel, \
    PRIMITIVE_TYPES as P_TYPES

collect = Sentinel('<collect object>')


class Runnable(object):
    ENTRY_POINT_NAME = None

    _cnt_subclasses = 0

    @classmethod
    def get_entry_point(cls):
        """
        :return str, callable:
        """
        if cls.ENTRY_POINT_NAME is None:
            raise RuntimeError('Runnable is not built by ClassFactory nor extended')
        return cls.ENTRY_POINT_NAME, getattr(cls, cls.ENTRY_POINT_NAME)

    @classmethod
    def ClassFactory(cls, f):
        """Wrap a function with a subclass of Runnable so that it is a qualified target.

        :param callable f:
        """
        cls._cnt_subclasses += 1
        cls_name = '_{}_{}'.format(cls.__name__, cls._cnt_subclasses)
        NewClass = type(cls_name, (cls,), {
            'ENTRY_POINT_NAME': f.__name__,
            f.__name__:         staticmethod(f),
        })
        return NewClass


class Executor(object):
    """Run the target and return the result."""
    _injected_targets = set()

    PRIMITIVE_TYPES = P_TYPES + tuple(
        filter(lambda x: isinstance(x, type), get_dependency().values()))

    def __init__(self, args, operation):
        self.is_operation = operation
        self.init_args, self.operation_stubs, self.collected = self.process_args(args, operation)
        self.initialized = False

    def initialize(self, target, post_proc=None, in_place_selector=None):
        self.target = target
        self.post_proc = post_proc or identity
        self.in_place_selector = in_place_selector
        self.initialized = True

    def make_operations(self, target):
        """
        :return [Operation]:
        """
        if isinstance(target, type):
            cls = target
        else:
            if callable(target):
                cls = Runnable.ClassFactory(target)
            else:
                raise ValueError('Target is not a class nor function')

        # Inject dependency such as TreeNode into user's solutions
        if target not in self._injected_targets:
            inject_dependency(target)
            self._injected_targets.add(target)

        o = cls(*self.init_args)
        ops = [stub.complete(o) for stub in self.operation_stubs]
        return ops

    def normalize_raw_output(self, output):
        return self.post_proc(self._normalize(output))

    def run(self, target=None):
        """Execute operations on the target.

        :param target: if specified, run on this target instead of the one specified by calling
            initialize()
        :return Result:
        """
        if not self.initialized:
            raise RuntimeError('Executor is not initialized')

        res = []

        with user_mode('Calling this method is not supported when judging'):
            operations = self.make_operations(target or self.target)
            for op in operations:
                args = deepcopy(op.args)
                output = op.func(*args)
                if not op.collect:
                    continue

                if self.in_place_selector:
                    output = self.in_place_selector(args)
                output = self.normalize_raw_output(output)

                res.append(Output(op.func_name, op.args, output))

        return Result(res, self.collected)

    @classmethod
    def process_args(cls, args, operation):
        """
        :param args: arguments passed to `self.target`, or a sequence of operations, each of which
            consists of a method name, which is followed by arguments grouped in a list. If a method
            does not take arguments, its corresponding method name in an operation could be followed
            by nothing.

            When using the second format of args, wherever a `collect` is placed after an
            operation, the value returned by executing the operation is collected into a
            `Result`. If no `collect` was specified, the value returned by the last operation
            is collected.
        :param operation: whether args are of the second format or of the first one
        :return (any, ...), [OperationStub], bool: the first returned value is arguments
            to be passed to the constructor of target. The second returned value is a list of
            `OperationStub`. The third returned value is a bool indicating whether `collect` is
            used in the operations or not
        """
        init_args = []
        stubs = []

        if operation:
            def push_stub():
                stubs.append(curr_stub[0])
                curr_stub[0] = OperationStub()

            def get_symbol():
                if isinstance(item, str):
                    return NEXT_NAME
                if isinstance(item, (list, tuple)):
                    return ARGS
                if item is collect:
                    return CLCT
                return item

            def exec_empty():
                raise ValueError('args is empty')

            def handle_init_args():
                init_args[:] = item

            def handle_next_name():
                push_stub()
                handle_name()

            def handle_name():
                curr_stub[0].name = item

            def handle_collect():
                curr_stub[0].collect = True
                push_stub()

            def handle_args():
                curr_stub[0].args = item

            END = object()
            NAME = 'init_name'
            NEXT_NAME = 'name'
            INIT_ARGS = 'init_args'
            ARGS = 'args'
            CLCT = 'collect'
            TRANS = {
                (INIT_ARGS, NAME):       [(NAME,), (NEXT_NAME, ARGS, CLCT), exec_empty],
                (NAME,):                 [(NEXT_NAME, ARGS, CLCT), nop],
                (NEXT_NAME, ARGS, CLCT): [(NEXT_NAME, ARGS, CLCT), (NEXT_NAME, CLCT), (NAME,),
                                          push_stub],
                (NEXT_NAME, CLCT):       [(NEXT_NAME, ARGS, CLCT), (NAME,), push_stub],
            }

            state = INIT_ARGS, NEXT_NAME
            curr_stub = [OperationStub()]
            args = list(args)
            args.append(END)

            for item in args:
                states = TRANS.get(state)
                assert states is not None, 'Invalid state'

                symbol = get_symbol()
                if symbol is END:
                    handler = states[-1]
                else:
                    try:
                        idx_next_state = state.index(symbol)
                    except ValueError:
                        REPRS = {
                            NAME:      'method name',
                            NEXT_NAME: 'method name',
                            INIT_ARGS: '__init__ args',
                            ARGS:      'arguments',
                            CLCT:      'collect object',
                        }
                        expected = natural_join('or', map(REPRS.get, state))
                        raise ValueError('expected {}, got {}'.format(expected, item))

                    handler = locals()['handle_' + symbol]
                    state = states[idx_next_state]
                handler()

            if not stubs:
                raise ValueError('Operations contains no method call')

            has_collect_obj = any(c is collect for c in args)
            if not has_collect_obj:
                # collect output of the last operation if no collect object was used
                stubs[-1].collect = True

        else:
            has_collect_obj = False
            stubs.append(OperationStub(None, args, True))

        return tuple(init_args), stubs, has_collect_obj

    @classmethod
    def _normalize(cls, output):
        if isinstance(output, cls.PRIMITIVE_TYPES) or output is None:
            pass
        elif is_iterable(output):
            output = [cls._normalize(o) for o in output]
        else:
            raise RuntimeError('Type of output {} is invalid'.format(type(output)))
        return output


class OperationStub(object):
    name = OneTimeSetProperty()
    args = OneTimeSetProperty(())
    collect = OneTimeSetProperty(False)

    def __init__(self, name=sentinel, args=sentinel, collect=sentinel):
        if name is not sentinel:
            self.name = name
        if args is not sentinel:
            self.args = args
        if collect is not sentinel:
            self.collect = collect

    def complete(self, obj):
        """
        :param obj: instance of target
        :return Operation:
        """
        name, method = self.get_method(obj)
        return Operation(name, method, self.args, self.collect)

    def get_method(self, obj):
        """Get from an object a method that will be called to get result of test cases.

        :return str, callable:
        """
        if isinstance(obj, Runnable):
            if self.name:
                raise ValueError("Cannot get methods other than 'run' from a Runnable instance")
            method = obj.get_entry_point()
        elif self.name:
            method = self.name, getattr(obj, self.name)
        else:
            # Guess a method
            methods = getmembers(obj, predicate=ismethod)
            methods = [(name, f) for name, f in methods if not name.startswith('_')]
            if len(methods) != 1:
                raise RuntimeError(
                    'Cannot find the target method. You may specify a list of operations as '
                    'arguments to Case if there are multiple methods to be called, or prepend all '
                    'names of private methods with underscores.')
            [method] = methods
        return method


class Operation(object):
    def __init__(self, func_name, func, args, collect):
        """
        :param str func_name: name of `func`
        :param callable func: a function to be called
        :param (any, ...) args: arguments to be called with
        :param bool collect: whether result of this operation should collect or not
        """
        self.func_name = func_name
        self.func = func
        self.args = args
        self.collect = collect


class Checkable(object):
    def __str__(self):
        raise NotImplementedError

    def check(self, x):
        raise NotImplementedError

    def success(self):
        raise NotImplementedError


class Output(Checkable):
    def __init__(self, func_name, args, val):
        """Output of executing an operation

        :param func_name: name of the function called
        :param args: arguments called with
        :param val: returned value of the function
        """
        self.func_name = func_name
        self.args = args
        self.val = val
        self.asserted_val = sentinel

    def __str__(self):
        repr_args = ', '.join(map(repr, self.args))
        if self.asserted_val is sentinel:
            repr_comparison = '?'
        else:
            op_eq = '==' if self.success() else '!='
            repr_comparison = '{} {} {}'.format(repr(self.val), op_eq, repr(self.asserted_val))
        return '{}({}) -> {}'.format(self.func_name, repr_args, repr_comparison)

    def success(self):
        if self.asserted_val is sentinel:
            raise RuntimeError('Output is not checked yet')
        return self.val == self.asserted_val

    def check(self, asserted_val):
        if self.asserted_val is sentinel:
            self.asserted_val = asserted_val
        return self.success()


class Result(Checkable):
    MAX_STR_ENTS = 4
    ABBR_ENTS = '...'

    def __init__(self, outputs, collected):
        """
        :param [Output] outputs:
        :param bool collected: whether outputs are collected or not
        """
        self.outputs = outputs
        self.collected = collected
        self.checked_outputs = []
        self.asserted_vals = sentinel
        self.result = None

    def __str__(self):
        if self.checked_outputs is None:
            msg = 'Result is not checked yet'
        else:
            if self.result:
                msg = 'Output equals asserted values'
            else:
                # Abbreviate outputs if there are too many
                if len(self.checked_outputs) > self.MAX_STR_ENTS:
                    entries = [self.ABBR_ENTS] + self.checked_outputs[-self.MAX_STR_ENTS + 1:]
                else:
                    entries = self.checked_outputs
                msg = '\n'.join(map(str, entries))
        return msg

    def success(self):
        if self.result is None:
            if self.asserted_vals is sentinel:
                raise RuntimeError('Result is not checked yet')

            for t_out, a_val in zip(self.outputs, self.asserted_vals):
                self.checked_outputs.append(t_out)
                if not t_out.check(a_val):
                    self.result = False
                    break
            else:
                self.result = True
        return self.result

    def check(self, asserted_vals):
        if self.asserted_vals is sentinel:
            if self.collected:
                # Not checking type, but matching pattern
                if not isinstance(asserted_vals, list) or not asserted_vals:
                    raise TypeError(
                        'Result should be an non-empty list when explicitly collecting output in '
                        'operations')
                self.asserted_vals = asserted_vals
            else:
                self.asserted_vals = [asserted_vals]
        return self.success()
