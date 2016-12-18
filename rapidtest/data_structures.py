from collections import deque
from itertools import count
from json import loads
from random import random

from .user_interfaces import privileged
from .utils import nop, randbool, randints


class Reprable(object):
    NULL = '#'

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self)

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
        return self._to_string(True)

    def _to_string(self, top_level=False):
        if self.left or self.right:
            str_left = self.left._to_string() if self.left else self.NULL
            str_right = self.right._to_string() if self.right else self.NULL
            res = '{}, {}, {}'.format(self.val, str_left, str_right)
            if not top_level:
                res = '({})'.format(res)
        else:
            res = str(self.val)
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
        """
        :return [int]: inorder traversal of nodes' values
        """
        return self.traverse_map(TreeNode.get_val, self.INORDER)

    @privileged
    def postorder(self):
        """
        :return [int]: postorder traversal of nodes' values
        """
        return self.traverse_map(TreeNode.get_val, self.POSTORDER)

    @privileged
    def preorder(self):
        """
        :return [int]: preorder traversal of nodes' values
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
        q = deque(vals)
        if not q:
            return None

        val = q.popleft()
        if val is None:
            raise ValueError('Root of tree cannot be None')
        root = cls(val)

        q = deque([root])
        while q and q:
            parent = q.popleft()

            val = q.popleft()
            if val is not None:
                parent.left = cls(val)
                q.append(parent.left)

            if not q:
                break
            val = q.popleft()
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
            if cnt_nones < cnt_nodes and randbool(1 - density):
                structured_vals.append(None)
                cnt_nones += 1
            else:
                structured_vals.append(vals[cnt_nodes])
                cnt_nodes += 1

        node = cls.from_iterable(structured_vals)

        if binary_search:
            def _repl_val(node):
                node.val = next(cnt)

            cnt = count()
            node.traverse_map(_repl_val, cls.INORDER)

        return node


class ListNode(Reprable):
    def __init__(self, x):
        self.val = x
        self.next = None

    def __str__(self):
        vals = list(self._gen())
        vals.append(self.NULL)
        return '{}'.format('->'.join(map(str, vals)))

    @privileged
    def __iter__(self):
        return self._gen()

    def _gen(self):
        """
        :return generator: generator that traverses self
        """
        while self:
            yield self.val
            self = self.next

    @privileged
    def end(self):
        """
        :return ListNode: last node in the list
        """
        while self.next:
            self = self.next
        return self

    @classmethod
    @privileged
    def from_iterable(cls, vals):
        vals = list(vals)
        if not vals:
            return None

        root = cls(vals[0])
        node = root
        for val in vals[1:]:
            node.next = cls(val)
            node = node.next
        return root

    @privileged
    def __eq__(self, o):
        while self and o:
            if self.val != o.val:
                return False
            self = self.next
            o = o.next
        return self is o is None
