import sys
from itertools import count
from random import randint, random, sample

if sys.version_info.major < 3:
    range = xrange


MAX_INT = 2 ** 31 - 1
MIN_INT = -(2 ** 31)


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
    if hasattr(o, '__len__'):
        return len(o)

    if is_iterable(o):
        o = iter(o)
        for i in count():
            try:
                next(o)
            except StopIteration:
                return i

    return 0


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


def identity(x):
    return x


def nop(*args, **kwargs):
    pass


def randints(count=20, unique=False, max_num=100, min_num=0):
    """Generate a list of random integers within the range [min_num, max_num]

    :param int count: how many integers are there in the list
    :param bool unique: whether generate no duplicates
    :param int max_num: maximum possible number in the list
    :param int min_num: minimum possible number in the list
    :return [int]:
    """
    count, min_num, max_num = map(int, (count, min_num, max_num))

    if unique:
        nums = sample(range(min_num, max_num + 1), count)
    else:
        nums = [randint(min_num, max_num) for _ in range(count)]

    return nums


def randbool(chance=0.5):
    """
    :param float chance: chance of returning True
    """
    if not (0 <= chance <= 1):
        raise ValueError('chance is not within the range [0, 1]')
    return random() < chance
