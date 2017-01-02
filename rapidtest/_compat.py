import inspect
import sys
from collections import Sequence

PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2

if PY3:
    # noinspection PyUnresolvedReferences
    import queue

    basestring = str

if PY2:
    # noinspection PyUnresolvedReferences
    from itertools import imap as map, izip as zip, ifilter as filter
    # noinspection PyUnresolvedReferences
    import Queue as queue

    range = xrange

def is_sequence(x):
    return isinstance(x, Sequence) and not isstring(x)


def isstring(x):
    return isinstance(x, basestring)


def with_metaclass(meta, *bases):
    """
    Function from jinja2/_compat.py. License: BSD.

    Use it like this::

        class BaseForm(object):
            pass

        class FormType(type):
            pass

        class Form(with_metaclass(FormType, BaseForm)):
            pass

    This requires a bit of explanation: the basic idea is to make a
    dummy metaclass for one level of class instantiation that replaces
    itself with the actual metaclass.  Because of internal type checks
    we also need to make sure that we downgrade the custom metaclass
    for one level to something closer to type (that's why __call__ and
    __init__ comes back from type etc.).

    This has the advantage over six.with_metaclass of not introducing
    dummy classes into the final MRO.
    """

    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)

    return metaclass('temporary_class', None, {})


def _get_caller_globals_and_locals():
    """
    Returns the globals and locals of the calling frame.

    Is there an alternative to frame hacking here?
    """
    caller_frame = inspect.stack()[2]
    myglobals = caller_frame[0].f_globals
    mylocals = caller_frame[0].f_locals
    return myglobals, mylocals


def _repr_strip(mystring):
    """
    Returns the string without any initial or final quotes.
    """
    r = repr(mystring)
    if r.startswith("'") and r.endswith("'"):
        return r[1:-1]
    else:
        return r


if PY3:
    def raise_from(exc, cause):
        """
        Equivalent to:

            raise EXCEPTION from CAUSE

        on Python 3. (See PEP 3134).
        """
        # Is either arg an exception class (e.g. IndexError) rather than
        # instance (e.g. IndexError('my message here')? If so, pass the
        # name of the class undisturbed through to "raise ... from ...".
        if isinstance(exc, type) and issubclass(exc, Exception):
            exc = exc.__name__
        if isinstance(cause, type) and issubclass(cause, Exception):
            cause = cause.__name__
        execstr = "raise " + _repr_strip(exc) + " from " + _repr_strip(cause)
        myglobals, mylocals = _get_caller_globals_and_locals()
        exec (execstr, myglobals, mylocals)


    def raise_(tp, value=None, tb=None):
        """
        A function that matches the Python 2.x ``raise`` statement. This
        allows re-raising exceptions with the cls value and traceback on
        Python 2 and 3.
        """
        if value is not None and isinstance(tp, Exception):
            raise TypeError("instance exception may not have a separate value")
        if value is not None:
            exc = tp(value)
        else:
            exc = tp
        if exc.__traceback__ is not tb:
            raise exc.with_traceback(tb)
        raise exc


    def raise_with_traceback(exc, traceback=Ellipsis):
        if traceback == Ellipsis:
            _, _, traceback = sys.exc_info()
        raise exc.with_traceback(traceback)

else:
    def raise_from(exc, cause):
        """
        Equivalent to:

            raise EXCEPTION from CAUSE

        on Python 3. (See PEP 3134).
        """
        # Is either arg an exception class (e.g. IndexError) rather than
        # instance (e.g. IndexError('my message here')? If so, pass the
        # name of the class undisturbed through to "raise ... from ...".
        if isinstance(exc, type) and issubclass(exc, Exception):
            e = exc()
            # exc = exc.__name__
            # execstr = "e = " + _repr_strip(exc) + "()"
            # myglobals, mylocals = _get_caller_globals_and_locals()
            # exec(execstr, myglobals, mylocals)
        else:
            e = exc
        e.__suppress_context__ = False
        if isinstance(cause, type) and issubclass(cause, Exception):
            e.__cause__ = cause()
            e.__suppress_context__ = True
        elif cause is None:
            e.__cause__ = None
            e.__suppress_context__ = True
        elif isinstance(cause, BaseException):
            e.__cause__ = cause
            e.__suppress_context__ = True
        else:
            raise TypeError("exception causes must derive from BaseException")
        e.__context__ = sys.exc_info()[1]
        raise e
