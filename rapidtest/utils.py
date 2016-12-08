from itertools import count


def rec_list(o):
    return rec_cast(list, o)


def rec_tuple(o):
    return rec_cast(tuple, o)


def rec_cast(f, o):
    if isinstance(o, (int, float, bool, str)):
        return o
    try:
        return f(rec_cast(f, i) for i in o)
    except TypeError:
        return o


unordered = sorted


def rec_unordered(o):
    return rec_cast(sorted, o)


def super_len(o):
    """May loop forever if o is an infinite generator."""
    try:
        return len(o)
    except Exception:
        pass

    if not is_iterable(o):
        return 0

    i = 0
    for i in count():
        try:
            next(o)
        except StopIteration:
            break
        except Exception:
            pass
    return i


def is_iterable(o):
    try:
        iter(o)
    except Exception:
        return False
    return True


def memo(f):
    """Can only cache hashable arguments."""
    def _f(*args, **kwargs):
        key = args, tuple(kwargs.items())
        try:
            return cache[key]
        except KeyError:
            result = cache[key] = f(*args, **kwargs)
            return result

    cache = {}

    return _f
