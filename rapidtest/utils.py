import string
from itertools import count, chain, combinations
from random import randint, random, sample, choice

from ._compat import isstring

sentinel = object()

MAX_INT = 2 ** 31 - 1
MIN_INT = -(2 ** 31)

PRIMITIVE_TYPES = int, float, bool, str


def rec_list(x):
    return rec_cast(list, x)


def rec_tuple(x):
    return rec_cast(tuple, x)


def rec_cast(f, x):
    if not isinstance(x, PRIMITIVE_TYPES) and iterable(x):
        return f(rec_cast(f, i) for i in x)
    return x


def unordered(x):
    if iterable(x):
        return sorted(x)
    return x


def rec_unordered(x):
    return rec_cast(unordered, x)


def super_len(x):
    """May loop forever if x is an infinite generator."""
    if lenable(x):
        return len(x)

    if iterable(x):
        iter_x = iter(x)
        for i in count():
            try:
                next(iter_x)
            except StopIteration:
                return i

    return 0


def iterable(x):
    return hasattr(x, '__iter__')


def lenable(x):
    return hasattr(x, '__len__')


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


# noinspection PyUnusedLocal
def nop(*args, **kwargs):
    pass


def randints(count=20, unique=False, max_num=100, min_num=0):
    """
    :param int count: how many integers are there in the list
    :param bool unique: whether generate no duplicates
    :param int max_num: maximum possible number in the list
    :param int min_num: minimum possible number in the list
    :return [int]: a `count` length/ list of random integers chosen from the range [min_num,
        max_num]
    """
    count, min_num, max_num = map(int, (count, min_num, max_num))
    return randlist(count, range(min_num, max_num + 1), unique)


def randbool(chance=0.5):
    """
    :param float chance: chance of returning True
    :return bool:
    """
    if not (0 <= chance <= 1):
        raise ValueError('chance is not within the range [0, 1]')
    return random() < chance


def randstr(length=None, unique=False, alphabet=string.ascii_lowercase):
    """
    :return: a random string
    """
    if length is None:
        length = randint(0, 100)
    else:
        length = int(length)
    return ''.join(randlist(length, alphabet, unique))


# noinspection PyIncorrectDocstring
def randlist(count, alphabet, unique=False):
    """Generate a list of symbols from alphabet

    :param bool unique: whether there will not be duplicates in returned list
    :return [type(alphabet), ...]: a `count` length list of random symbols chosen from `alphabet`
    """
    if unique:
        res = sample(alphabet, count)
    else:
        res = [choice(alphabet) for _ in range(count)]
    return res


class OneTimeSetProperty(object):
    """Property that can only be changed once.
    If `default` is not specified and this property is never set, getting it will cause an
    Exception.
    """
    cnt_props = 0

    def __init__(self, default=sentinel):
        self.name = '_{}_{}'.format(type(self).__name__, self.cnt_props)
        type(self).cnt_props += 1

        self.default = default

    def __get__(self, instance, owner):
        x = getattr(instance, self.name, self.default)
        if x is sentinel:
            raise AttributeError('Property is not set yet')
        return x

    def __set__(self, instance, value):
        if hasattr(instance, self.name):
            raise AttributeError('Cannot reset attribute')
        setattr(instance, self.name, value)

    def __delete__(self, instance):
        raise AttributeError('Cannot delete attribute')


class Reprable(object):
    NAME = None

    def __repr__(self):
        return '{}({})'.format(self.NAME or type(self).__name__, self)

    def __str__(self):
        raise NotImplementedError


class Sentinel(Reprable):
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)


def natural_join(last_sep, strs):
    """Join strs as if in a natural sentence."""
    strs = list(strs)
    if not all(map(isstring, strs)):
        raise TypeError('Some of strs is not of type str')

    if not strs:
        return ''
    if len(strs) == 1:
        return strs[0]
    if len(strs) == 2:
        l, r = strs
        return ' '.join([l, last_sep, r])
    strs[-1] = '{} {}'.format(last_sep, strs[-1])
    return ', '.join(strs)


def natural_format(fmt, *args, **kwargs):
    """Format by plurality of item.

    :param str fmt:
    :param iterable item:
    :param str last_sep: defaults to 'and'
    """
    item = kwargs.get('item')
    if item is None:
        raise TypeError(natural_join.__name__ + "() missing 1 required keyword argument: 'item'")
    if not iterable(item):
        raise TypeError("'item' is not iterable")

    item = list(map(str, item))
    if len(item) == 0:
        raise ValueError("'item' is empty")
    plural = len(item) != 1
    last_sep = kwargs.get('last_sep', 'and')
    return fmt.format(*args,
                      item=natural_join(last_sep, item),
                      a='' if plural else 'a ',
                      an='' if plural else 'an ',
                      s='s' if plural else '',
                      es='es' if plural else '')


def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
