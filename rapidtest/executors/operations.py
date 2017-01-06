from .outputs import OperationOutput
from .rpc import Request
from .rpc.utils import JsonSerializable, ExternalObject


class Operation(JsonSerializable):
    def __init__(self, name=None, args=(), collect=False):
        """
        :param str|None name: name of function
        :param Tuple[Any, ...] args:
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

    def as_output(self, val):
        return OperationOutput(self.name, self.args, self.collect, val)

    def as_json_object(self, target=None):
        # Inject class name
        return Request([target, self.name], self.args).as_json_object()


class Operations(JsonSerializable):
    def __init__(self, init_args, operations, post_proc=None, in_place_selector=None):
        self.init_args = init_args
        self.operations = operations
        self.post_proc = post_proc
        self.in_place_selector = in_place_selector
        self.target_name = None

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

    def set_target_name(self, name):
        """For the purpose of instantiating target in external executor.

        :param str name:
        """
        self.target_name = name

    def as_attributes(self):
        assert self.target_name is not None
        return {
            'in_place':        bool(self.in_place_selector),
            'target_instance': ExternalObject(self.target_name, self.init_args).as_json_object(),
            'operations':      [o.as_json_object(self.target_name) for o in self.operations],
        }

    def update_operation_names(self, names):
        """
        :param List[str] names:
        """
        assert len(names) == len(self.operations)
        for name, op in zip(names, self.operations):
            op.name = name
