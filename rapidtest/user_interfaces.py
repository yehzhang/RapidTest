from collections import deque
from contextlib import contextmanager
from inspect import getmodule
from itertools import count
from json import loads
from random import random

from .utils import nop, randbool, randints

_kernel_mode = True
_privilege_violation_msg = None


@contextmanager
def user_mode(msg=None):
    """Prevent running privileged functions in this context.

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


def privileged(f):
    """Mark a function as privileged."""
    def _f(*args, **kwargs):
        if not _kernel_mode:
            msg = 'Using this feature is unsupported' if _privilege_violation_msg is None else \
                _privilege_violation_msg
            raise RuntimeError(msg)
        return f(*args, **kwargs)

    return _f


class Reprable(object):
    NULL = '#'

    def __repr__(self):
        return '{}{}'.format(type(self).__name__, self)

    def __str__(self):
        raise NotImplementedError


class TreeNode(Reprable):
    INORDER = 'inorder'
    PREORDER = 'preorder'
    POSTORDER = 'postorder'

    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

    @privileged
    def __eq__(self, o):
        return self._eq(o)

    def _eq(self, o):
        return o and self.val == o.val and self.left and self.left._eq(
            o.left) and self.right and self.right._eq(o.right)

    def __str__(self):
        return self._to_string()

    def _to_string(self, top_level=True):
        if self.left or self.right:
            str_left = self.left._to_string(False) if self.left else self.NULL
            str_right = self.right._to_string(False) if self.right else self.NULL
            res = '({}, {}, {})'.format(self.val, str_left, str_right)
        else:
            res = ('({})' if top_level else '{}').format(self.val)
        return res

    def get_val(self):
        return self.val

    @privileged
    def traverse_map(self, function, order=INORDER):
        """Apply function to every node in the given order, and return a list of the results.

        :param function: a function that takes a TreeNode and returns a result
        :param order: either TreeNode.INORDER, TreeNode.PREORDER, or TreeNode.POSTORDER
        :return [any]:
        """

        def _map_wrapper(f):
            def _f(node):
                res.append(f(node))

            return _f

        res = []

        stack = []
        node = self

        if order in (self.INORDER, self.PREORDER):
            if order == self.INORDER:
                inorder, preorder = _map_wrapper(function), nop
            else:
                inorder, preorder = nop, _map_wrapper(function)

            while node or stack:
                while node:
                    preorder(node)
                    stack.append(node)
                    node = node.left
                node = stack.pop()
                inorder(node)
                node = node.right

        elif order == self.POSTORDER:
            def _post_trav(node):
                if node:
                    _post_trav(node.left)
                    _post_trav(node.right)
                    postorder(node)

            postorder = _map_wrapper(function)
            _post_trav(node)

        else:
            raise TypeError('order is not one of the accepted orders')

        return res

    @privileged
    def inorder(self):
        """Return inorder traversal of nodes' values

        :return [int]:
        """
        return self.traverse_map(TreeNode.get_val, self.INORDER)

    @privileged
    def postorder(self):
        """Return postorder traversal of nodes' values

        :return [int]:
        """
        return self.traverse_map(TreeNode.get_val, self.POSTORDER)

    @privileged
    def preorder(self):
        """Return preorder traversal of nodes' values

        :return [int]:
        """
        return self.traverse_map(TreeNode.get_val, self.PREORDER)

    @privileged
    def flatten(self):
        """
        :return [int]:
        """
        raise NotImplementedError

    @classmethod
    @privileged
    def from_iterable(cls, vals):
        try:
            vals = deque(vals)
        except TypeError:
            raise TypeError('vals is not an iterable')

        if not vals:
            return None

        val = vals.popleft()
        if val is None:
            raise ValueError('Root of tree cannot be None')
        root = cls(val)

        q = deque([root])
        while q and vals:
            parent = q.popleft()

            val = vals.popleft()
            if val is not None:
                parent.left = cls(val)
                q.append(parent.left)

            if not vals:
                break
            val = vals.popleft()
            if val is not None:
                parent.right = cls(val)
                q.append(parent.right)

        return root

    @classmethod
    @privileged
    def from_string(cls, vals):
        try:
            vals = loads(vals)
        except (ValueError, TypeError):
            raise ValueError('vals is not a json string representing an array of values')

        return cls.from_iterable(vals)

    @classmethod
    @privileged
    def make_random(cls, num_nodes=100, binary_search=False):
        """
        :param int num_nodes: number of nodes in the tree
        :param bool binary_search: whether return a binary search tree or simply a binary tree
        :return TreeNode:
        """
        num_nodes = int(num_nodes)
        if binary_search:
            vals = [0] * num_nodes  # just a placeholder array
        else:
            vals = randints(num_nodes)

        # Randomize structure
        structured_vals = []
        cnt_nones = 0
        cnt_nodes = 0
        density = random() * 0.9 + 0.1  # lower density -> higher tree
        while cnt_nodes < len(vals):
            # Prevent the tree from broken
            if cnt_nones < cnt_nodes and not randbool(density):
                structured_vals.append(None)
                cnt_nones += 1
            else:
                structured_vals.append(vals[cnt_nodes])
                cnt_nodes += 1

        node = cls(structured_vals)

        if binary_search:
            def _repl_val(node):
                node.val = next(cnt)

            cnt = count()
            node.traverse_map(_repl_val, cls.INORDER)

        return node


def inject_dependency(o):
    module = getmodule(o)
    if module is None:
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
