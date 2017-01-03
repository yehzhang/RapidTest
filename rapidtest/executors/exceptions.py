from ..utils import Dictable

MSG_CANNOT_GUESS_METHOD = '''cannot find the target method. You may specify operations as \
arguments to Case if there are multiple methods to be called, or prepend all names of private \
methods with underscores.'''


class ExternalError(Exception):
    pass


class ExternalEnvironmentError(ExternalError):
    pass


class ExternalRuntimeError(ExternalError):
    pass


class ExternalException(Dictable):
    def __init__(self, name, message=None, stack_trace=None, runtime=False):
        self.name = name
        self.message = message or ''
        self.stack_trace = (stack_trace or '').rstrip()
        self.runtime = runtime

    def to_exception(self):
        Exc = type(self.name, (Exception,), {})
        msg = '{}\n{}'.format(self.message, self.stack_trace)
        Wrapper = ExternalRuntimeError if self.runtime else ExternalEnvironmentError
        return Wrapper, Exc(msg)
