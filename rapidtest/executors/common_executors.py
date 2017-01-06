from .outputs import ExecutionOutput
from .._compat import is_sequence, PRIMITIVE_TYPES as P_TYPES
from ..utils import identity


class BaseExecutor(object):
    ENVIRONMENT = None

    PRIMITIVE_TYPES = P_TYPES

    def __init__(self, target):
        self.target = target
        self.initialize()

    def initialize(self, post_proc=None, in_place_selector=None):
        self.in_place_selector = in_place_selector
        self.post_proc = post_proc or identity

    def execute(self, operations):
        """
        :param Operations operations:
        :return ExecutionOutput:
        """
        operations.initialize(self)
        return ExecutionOutput(self.execute_operations(operations))

    def execute_operations(self, operations):
        """
        :param Operations operations:
        :return Iterable[OperationOutput]:
        """
        raise NotImplementedError

    def finalize_operation(self, operation, output):
        """
        :param Operation operation:
        :param Any output: returned value from the operation
        :return OperationOutput:
        """
        if self.in_place_selector:
            output = self.in_place_selector(output)
        output = self.normalize_raw(output)
        return operation.as_output(output)

    def normalize_raw(self, val):
        return self.post_proc(self._normalize_type(val))

    @classmethod
    def _normalize_type(cls, val):
        if isinstance(val, cls.PRIMITIVE_TYPES) or val is None:
            pass
        elif is_sequence(val):
            val = [cls._normalize_type(o) for o in val]
        else:
            raise RuntimeError('type of return value {} is invalid'.format(type(val)))
        return val
