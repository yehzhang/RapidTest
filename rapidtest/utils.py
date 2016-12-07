from collections import deque
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


class TreeNode(object):
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

    def __eq__(self, o):
        return isinstance(o, type(self)) and self.val == o.val

    def __repr__(self):
        return '{}{}'.format(type(self).__name__, self)

    def __str__(self):
        return '({}, {}, {})'.format(self.val, self.left or '#', self.right or '#') \
            if self.left or self.right else str(self.val)


class Tree(object):
    def __init__(self, vals):
        vals = list(vals)

        if vals:
            assert vals[0] is not None, 'Root of tree cannot be None'
            self.root = TreeNode(vals[0])

            q = deque([self.root])
            i = 1
            while q and i < len(vals):
                parent = q.popleft()

                if vals[i] is not None:
                    parent.left = TreeNode(vals[i])
                    q.append(parent.left)
                i += 1

                if not i < len(vals):
                    break
                if vals[i] is not None:
                    parent.right = TreeNode(vals[i])
                    q.append(parent.right)
                i += 1

        else:
            self.root = None

    @classmethod
    def make_root(cls, *args, **kwargs):
        t = cls(*args, **kwargs)
        return t.root


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


def from_none(exc):
    """Suppress cause of an exception."""
    exc.__cause__ = None
    return exc
