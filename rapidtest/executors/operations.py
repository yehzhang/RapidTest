from .clients import Request
from .outputs import OperationOutput


class Operation(object):
    def __init__(self, name=None, args=(), collect=False):
        """
        :param str|None name: name of function
        :param (any, ...) args:
        :param bool collect:
        """
        self.name = name
        self.args = args
        self.collect = collect

    def __str__(self):
        repr_output = ' -> ?' if self.collect else ''
        return OperationOutput.format(self.name or '?', self.args, repr_output)

    def __eq__(self, other):
        """For testing. """
        return isinstance(other, type(
            self)) and self.name == other.name and self.args == other.args and self.collect == \
                                                                               other.collect

    def to_output(self, val):
        return OperationOutput(self.name, self.args, self.collect, val)

    def to_request(self):
        return Request(self.name, self.args)


class Operations(object):
    def __init__(self, init_args, operations, post_proc=None, in_place_selector=None):
        self.init_args = init_args
        self.operations = operations
        self.post_proc = post_proc
        self.in_place_selector = in_place_selector

    def __iter__(self):
        return iter(self.operations)

    def __len__(self):
        return len(self.operations)

    def __eq__(self, other):
        """For testing. """
        return isinstance(other, type(self)) and self.init_args == other.init_args and len(
            self) == len(other) and all(s == o for s, o in zip(self, other))

    def initialize(self, executor):
        executor.initialize(post_proc=self.post_proc, in_place_selector=self.in_place_selector)

    def to_params(self):
        """
        :return [any]): params
        """
        params = [{
            'in_place': bool(self.in_place_selector)
        }, dict(Request(params=self.init_args))]
        params.extend(dict(o.to_request()) for o in self.operations)
        return params
