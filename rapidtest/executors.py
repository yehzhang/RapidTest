# coding=utf-8
from copy import deepcopy
from inspect import getmembers, ismethod, isclass

from .user_interface import inject_dependency, get_dependency, user_mode
from .utils import is_iterable, identity, OneTimeSetProperty, sentinel, PRIMITIVE_TYPES as \
    P_TYPES, \
    indent, get_func


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
        return cls.ENTRY_POINT_NAME, get_func(cls, cls.ENTRY_POINT_NAME)

    @classmethod
    def ClassFactory(cls, f):
        """Wrap a function with a subclass of Runnable so that it is a qualified target.

        :param function f:
        """
        cls._cnt_subclasses += 1
        cls_name = '_{}_subclass_{}'.format(cls.__name__, cls._cnt_subclasses)
        NewClass = type(cls_name, (cls,), {
            'ENTRY_POINT_NAME': f.__name__,
            f.__name__:         staticmethod(f),
        })
        return NewClass


class Executor(object):
    """Provide a strategies for lazy-evaluating operations.

    :param [OperationStub] operation_stubs:
    :param callable post_proc:
    :param callable in_place_selector:
    """
    _injected_targets = set()

    PRIMITIVE_TYPES = P_TYPES + tuple(v for v in get_dependency().values() if isclass(v))

    def __init__(self, init_args, operation_stubs, post_proc=None, in_place_selector=None):
        self.init_args = init_args
        self.operation_stubs = operation_stubs
        self.post_proc = post_proc or identity
        self.in_place_selector = in_place_selector

    def execute(self, target):
        """Execute operations on the target.

        :param type target:
        :return ExecutionOutput:
        """
        if not isclass(target):
            raise ValueError('Target is not a class')

        # Inject dependency such as TreeNode into user's solutions
        if target not in self._injected_targets:
            inject_dependency(target)
            self._injected_targets.add(target)

        with user_mode():
            target_instance = target(*self.init_args)

        # Lazy-executing operations
        ops = (self._execute(stub, target_instance) for stub in self.operation_stubs)
        return ExecutionOutput(ops)

    def _execute(self, stub, target_instance):
        """
        :param OperationStub stub:
        :return OperationOutput:
        """
        with user_mode():
            called_func_name, func = self.get_target_method(target_instance, stub.name)
            args = deepcopy(stub.args)
            val = func(*args)

            if stub.collect:
                if self.in_place_selector:
                    val = self.in_place_selector(args)
                val = self.normalize_raw_output(val)

        return OperationOutput(called_func_name, stub.args, stub.collect, val)

    def normalize_raw_output(self, output):
        return self.post_proc(self._normalize(output))

    @classmethod
    def get_target_method(cls, target_instance, name=None):
        """Get from `target_instance` a method and its name.

        :param object target_instance:
        :param str name: ignored if target is Runnable. If not specified and target is not Runnable,
            return the only public method, if any.
        :return str, callable:
        """
        if isinstance(target_instance, Runnable):
            method = target_instance.get_entry_point()
        elif name:
            method = name, get_func(target_instance, name)
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

    def __eq__(self, other):
        return isinstance(other, type(
            self)) and self.name == other.name and self.args == other.args and self.collect == \
                                                                               other.collect

    def __str__(self):
        repr_res = ' -> ?' if self.collect else ''
        return '{}({}){}'.format(self.name, OperationOutput.join_repr(self.args), repr_res)


class Output(object):
    def __str__(self):
        raise NotImplementedError

    def check(self, val):
        """Check equality of val against output

        :return bool:
        """
        raise NotImplementedError

    def get_val(self):
        """Do not check. Simply return the value of output. """
        raise NotImplementedError


class OperationOutput(Output):
    def __init__(self, func_name, args, collect, val=sentinel):
        """
        :param str func_name: name of function from target to be called. Ignored if target is
            Runnable
        :param (any, ...) args: arguments to be called with
        :param bool collect: whether returned value of this operation is collected or not
        :param any val: returned value of this operation. Required iff collect is True
        """
        self.func_name = func_name
        self.args = args
        self.collect = collect
        if collect:
            if val is sentinel:
                raise RuntimeError('Operation output is collected but val is not specified')
            self.val = val
            self.asserted_val = sentinel
            self.result = None

    def __str__(self):
        repr_args = self.join_repr(self.args)

        if self.collect:
            if self.asserted_val is sentinel:
                repr_comp = '?'
            else:
                repr_comp = '√' if self.result else '!= {}'.format(repr(self.asserted_val))
            repr_output = ' -> {} {}'.format(repr(self.val), repr_comp)
        else:
            repr_output = ''

        return '{}({}){}'.format(self.func_name, repr_args, repr_output)

    def get_val(self):
        if not self.collect:
            raise RuntimeError('Returned value was not collected')
        return self.val

    def check(self, asserted_val):
        val = self.get_val()
        self.asserted_val = asserted_val
        self.result = val == self.asserted_val
        return self.result

    @staticmethod
    def join_repr(strs):
        return ', '.join(map(repr, strs))


class ExecutionOutput(Output):
    MAX_ENT_LNS = 4
    ABBR_ENTS = '...'

    def __init__(self, operations):
        """
        :param iterable operations: a list or generator of OperationOutput
        """
        self._checked_outputs = []
        self._pending_outputs = iter(operations)
        self.result = None

    def __str__(self):
        """String representation of current state of result."""

        def abbr(ents, trim_bottom=False):
            if ents:
                # Abbreviate outputs if there are too many
                if len(ents) > self.MAX_ENT_LNS:
                    if trim_bottom:
                        i_start = 0
                        i_end = self.MAX_ENT_LNS
                        i_abbr = -1
                    else:  # trim_top
                        i_end = len(ents)
                        i_start = i_end - self.MAX_ENT_LNS
                        i_abbr = 0
                    ents = ents[i_start:i_end]
                    ents[i_abbr] = self.ABBR_ENTS
                entries.append('\n' + '\n'.join(map(indent, ents)))
            else:
                entries.append('no operations')

        entries = []

        if self.result is None:
            entries.append('output has not been completely checked: ')

            # Populate _checked_outputs with entries to be displayed
            for _ in zip(range(self.MAX_ENT_LNS + 1), self):
                pass

            abbr(self._checked_outputs, True)
        elif self.result is False:
            entries.append('output differs: ')

            # Display until failure
            i_end = len(self._checked_outputs)
            for i, o in enumerate(self._checked_outputs, 1):
                if o.collect and not o.result:
                    i_end = i
                    break
            abbr(self._checked_outputs[:i_end])
        else:  # self.result is True
            entries.append('output equals: ')
            abbr(self._checked_outputs)

        return ''.join(entries)

    def __iter__(self):
        """Iterate through all outputs."""
        i = 0

        while True:
            while i < len(self._checked_outputs):
                yield self._checked_outputs[i]
                i += 1
            try:
                o = next(self._pending_outputs)
            except StopIteration:
                break
            self._checked_outputs.append(o)

    def check(self, asserted_vals):
        self.result = None

        # assert len(asserted_vals) == len(total outputs)
        q_vals = iter(asserted_vals)
        for o in self:
            if o.collect:
                asserted_val = next(q_vals)
                if not o.check(asserted_val):
                    self.result = False
                    break
        else:
            self.result = True

        return self.result

    def get_val(self):
        return (o.get_val() for o in self if o.collect)
