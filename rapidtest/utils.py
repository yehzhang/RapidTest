from itertools import count
from random import randint, random, sample


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


def identity(x):
    return x


def nop(*args, **kwargs):
    pass


def randlist(count=20, sorted=False, unique=False, max_num=100, min_num=0):
    """Generate a list of random integers within the range [min_num, max_num]

    :param bool count: how many integers are there in the list
    :param bool sorted:
    :param bool unique: whether generate no duplicates
    :return [int]:
    """
    count, min_num, max_num = map(int, (count, min_num, max_num))

    if unique:
        nums = sample(range(min_num, max_num + 1), count)
    else:
        nums = [randint(min_num, max_num) for _ in range(count)]

    if sorted:
        nums.sort()

    return nums


def randbool(chance=0.5):
    """
    :param float chance: chance of returning True
    """
    if not (0 <= chance <= 1):
        raise ValueError('chance is not within the range [0, 1]')
    return random() < chance
