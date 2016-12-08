from sys import modules
from random import randint, shuffle
from collections import deque
from contextlib import contextmanager

_sentinel = object()

_kernel_mode = True
_privilege_violation_msg = None

@contextmanager
def user_mode(msg=None):
    """
    :param str msg: message to warn user about when privilege is violated
    """
    global _kernel_mode, _privilege_violation_msg
    if not _kernel_mode:
        raise RuntimeError('Already in user mode')

    if msg is not None:
        _privilege_violation_msg = msg
    _kernel_mode = False
    yield
    _kernel_mode = True
    _privilege_violation_msg = None


def _require_privilege():
    if not _kernel_mode:
        msg = 'Using this feature is unsupported' if _privilege_violation_msg is None else _privilege_violation_msg
        raise RuntimeError(msg)


class TreeNode(object):
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

    def __eq__(self, o):
        _require_privilege()
        return all(hasattr(o, k) for k in ('val', 'left', 'right')) and \
            self.val == o.val and self.left == o.left and self.right == o.right

    def __repr__(self):
        return '{}{}'.format(type(self).__name__, self)

    def __str__(self):
        return '({}, {}, {})'.format(self.val, self.left or '#', self.right or '#') \
            if self.left or self.right else '({})'.format(self)


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

    def inorder(self):
        """
        :return [int]:
        """
        pass

    def postorder(self):
        """
        :return [int]:
        """
        pass

    def preorder(self):
        """
        :return [int]:
        """
        pass

    def flatten(self):
        """
        :return [int]:
        """
        pass

    @classmethod
    def make_root(cls, *args, **kwargs):
        """
        :return TreeNode:
        """
        return cls(*args, **kwargs).root

    @classmethod
    def make_random(cls, num_nodes=100):
        """
        :return Tree:
        """
        pass

    @classmethod
    def make_random_binary_search(cls, num_nodes=100):
        """
        :return Tree:
        """
        pass

def inject_dependency(o):
    module_name = getattr(o, '__module__', _sentinel)
    module = modules.get(module_name, _sentinel)
    if module is _sentinel:
        return

    for name in DEPENDENCY_NAMES:
        if not hasattr(module, name):
            setattr(module, name, globals()[name])

def get_dependency():
    return [globals()[name] for name in DEPENDENCY_NAMES]

DEPENDENCY_NAMES = 'TreeNode',

try:
    get_dependency()
except Exception:
    assert False, 'Missing dependency'
