from rapidtest.utils import Dictable

MSG_CANNOT_GUESS_METHOD = '''\
cannot find the target method. You may use operations if there are multiple methods to be called, \
or make sure that there is only one public method in the target class.\
'''


class ExternalError(Exception):
    pass


class ExternalTargetError(ExternalError):
    pass


class TimeoutError(OSError):
    pass


class ExternalException(Dictable):
    def __init__(self, name, message=None, stack_trace=None, from_target=False):
        self.name = str(name)
        self.message = message or ''
        self.stack_trace = (stack_trace or '').rstrip()
        self.from_target = from_target

    def to_exceptions(self):
        Exc = type(self.name, (Exception,), {})
        msg = '{}\n{}'.format(self.message, self.stack_trace)
        exc = ExternalTargetError(
            'external target raised an exception') if self.from_target else \
            ExternalError('exception raised while executing external target')
        return exc, Exc(msg)
