from collections import deque
from contextlib import contextmanager
from inspect import getmodule
from itertools import count
from json import loads
from random import random

from .utils import nop, randbool

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
        msg = 'Using this feature is unsupported' if _privilege_violation_msg is None else \
            _privilege_violation_msg
        raise RuntimeError(msg)


class TreeNode(object):
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

    def __eq__(self, o):
        _require_privilege()
        return all(hasattr(o, k) for k in ('val', 'left',
                                           'right')) and self.val == o.val and self.left == \
                                                                               o.left and \
               self.right == o.right

    def __repr__(self):
        return '{}{}'.format(type(self).__name__, self)

    def __str__(self):
        return self._to_string()

    def _to_string(self, top_level=True):
        if self.left or self.right:
            str_left = self.left._to_string(False) if self.left else '#'
            str_right = self.right._to_string(False) if self.right else '#'
            res = '({}, {}, {})'.format(self.val, str_left, str_right)
        else:
            res = ('({})' if top_level else '{}').format(self.val)
        return res

    def get_val(self):
        return self.val


class Tree(object):
    """
    :param vals: an array of values, or a json string that contains an array of values
    """

    INORDER = 'inorder'
    PREORDER = 'preorder'
    POSTORDER = 'postorder'

    def __init__(self, vals):
        try:
            if isinstance(vals, str):
                vals = loads(vals)
            vals = list(vals)
        except (ValueError, TypeError):
            raise ValueError('vals is not an array of values nor a json string containing that')

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

    def __repr__(self):
        return '{}{}'.format(type(self).__name__, self.root)

    def __str__(self):
        return str(self.root)

    def traverse_map(self, function, order=INORDER):
        """Apply function to every node in the given order, and return a list of the results.

        :param function: a function that takes a TreeNode and returns a result
        :param order: either Tree.INORDER, Tree.PREORDER, or Tree.POSTORDER
        :return [any]:
        """

        def _map_wrapper(f):
            def _f(node):
                res.append(f(node))

            return _f

        res = []

        stack = []
        node = self.root

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

    def inorder(self):
        """Return inorder traversal of nodes' values

        :return [int]:
        """
        return self.traverse_map(TreeNode.get_val, self.INORDER)

    def postorder(self):
        """Return postorder traversal of nodes' values

        :return [int]:
        """
        return self.traverse_map(TreeNode.get_val, self.POSTORDER)

    def preorder(self):
        """Return preorder traversal of nodes' values

        :return [int]:
        """
        return self.traverse_map(TreeNode.get_val, self.PREORDER)

    def flatten(self):
        """
        :return [int]:
        """
        raise NotImplementedError

    @classmethod
    def make_root(cls, *args, **kwargs):
        """
        :return TreeNode:
        """
        return cls(*args, **kwargs).root

    @classmethod
    def make_random(cls, num_nodes=100, binary_search=False):
        """
        :param int num_nodes: number of nodes in the tree
        :param bool binary_search: whether return a binary search tree or simply a binary tree
        :return Tree:
        """
        num_nodes = int(num_nodes)
        if binary_search:
            vals = [0] * num_nodes  # just a placeholder array
        else:
            vals = list(range(num_nodes))

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

        tree = cls(structured_vals)

        if binary_search:
            def _repl_val(node):
                node.val = next(cnt)

            cnt = count()
            tree.traverse_map(_repl_val, Tree.INORDER)

        return tree


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
