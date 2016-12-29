# coding=utf-8
from ..utils import is_sequence, PRIMITIVE_TYPES as P_TYPES, identity


class BaseExecutor(object):
    PRIMITIVE_TYPES = P_TYPES

    def __init__(self, **kwargs):
        self.in_place_selector = None
        self.post_proc = identity

        self.initialize(**kwargs)

    def initialize(self, post_proc=None, in_place_selector=None):
        """
        :param callable post_proc:
        :param callable in_place_selector:
        """
        if post_proc is not None:
            self.post_proc = post_proc
        if in_place_selector is not None:
            self.in_place_selector = in_place_selector

    def execute(self, operations):
        """
        :param Operations operations:
        :return ExecutionOutput:
        """
        raise NotImplementedError

    def normalize_raw_output(self, output):
        return self.post_proc(self._normalize(output))

    @classmethod
    def _normalize(cls, output):
        if isinstance(output, cls.PRIMITIVE_TYPES) or output is None:
            pass
        elif is_sequence(output):
            output = [cls._normalize(o) for o in output]
        else:
            raise RuntimeError('Type of output {} is invalid'.format(type(output)))
        return output


class ExternalExecutor(BaseExecutor):
    pass


class CompiledExecutor(ExternalExecutor):
    def compile(self):
        pass
