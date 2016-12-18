import sys
from itertools import count
from random import randint, random, sample

if sys.version_info.major < 3:
    range = xrange


MAX_INT = 2 ** 31 - 1
MIN_INT = -(2 ** 31)


def rec_list(x):
    return rec_cast(list, x)


def rec_tuple(x):
    return rec_cast(tuple, x)


def rec_cast(f, x):
    if isinstance(x, (int, float, bool, str)):
        return x
    try:
        return f(rec_cast(f, i) for i in x)
    except TypeError:
        return x


unordered = sorted


def rec_unordered(x):
    return rec_cast(unordered, x)


def super_len(x):
    """May loop forever if x is an infinite generator."""
    if hasattr(x, '__len__'):
        return len(x)

    if hasattr(x, '__iter__'):
        for i in count():
            try:
                next(x)
            except StopIteration:
                return i

    return 0


def is_iterable(x):
    try:
        iter(x)
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
