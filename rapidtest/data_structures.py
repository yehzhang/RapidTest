from collections import deque
from importlib import import_module
from itertools import count
from json import loads
from random import random

from .executors.python.dependencies import TreeNode as BaseTreeNode, ListNode as BaseListNode
from .executors.rpc.utils import JsonSerializable
from .utils import nop, randbool, randints


def get_dependencies():
    """
    :return Dict[str, type]: {class_name: class}
    """
    dependencies = {}
    pkg_name, _ = __name__.rsplit('.', 1)
    for module_name, obj_names in PY_DEPENDENCY_NAMES.items():
        module = import_module(module_name, pkg_name)
        for obj_name in obj_names:
            obj = getattr(module, obj_name)
            dependencies[obj_name] = obj
    return dependencies


PY_DEPENDENCY_NAMES = {
    __name__: ['TreeNode', 'ListNode'],
}


class SerializableDataStructure(JsonSerializable):
    def as_constructor_params(self):
        return [self.flatten()]

    def get_external_name(self):
        name, _ = super(SerializableDataStructure, self).get_external_name()
        return name, 'from_iterable'

    def flatten(self):
        raise NotImplementedError


class TreeNode(BaseTreeNode, SerializableDataStructure):
    INORDER = 'inorder'
    PREORDER = 'preorder'
    POSTORDER = 'postorder'

    def __eq__(self, o):
        return o and self.val == o.val and self.left == o.left and self.right == o.right

    def get_val(self):
        return self.val

    def traverse_map(self, function, order=INORDER):
        """Apply function to every node in the given order, and return a list of the results.

        :param function: a function that takes a TreeNode and returns a result
        :param order: either TreeNode.INORDER, TreeNode.PREORDER, or TreeNode.POSTORDER
        :return List[Any]:
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

    def inorder(self):
        """
        :return List[int]: inorder traversal of nodes' values
        """
        return self.traverse_map(type(self).get_val, self.INORDER)

    def postorder(self):
        """
        :return List[int]: postorder traversal of nodes' values
        """
        return self.traverse_map(type(self).get_val, self.POSTORDER)

    def preorder(self):
        """
        :return List[int]: preorder traversal of nodes' values
        """
        return self.traverse_map(type(self).get_val, self.PREORDER)

    def flatten(self):
        """Inverse function of TreeNode.from_iterable

        :return List[int|None]:
        """
        vals = []

        q_nodes = deque([self])
        while q_nodes:
            parent = q_nodes.popleft()
            if parent is None:
                vals.append(None)
            else:
                vals.append(parent.val)
                q_nodes.append(parent.left)
                q_nodes.append(parent.right)

        while vals[-1] is None:
            vals.pop()

        return vals

    @classmethod
    def from_iterable(cls, vals):
        q_vals = deque(vals)
        if not q_vals:
            return None

        val = q_vals.popleft()
        if val is None:
            raise ValueError('root of tree cannot be None')
        root = cls(val)

        q_nodes = deque([root])
        while q_vals and q_nodes:
            parent = q_nodes.popleft()

            val = q_vals.popleft()
            if val is not None:
                parent.left = cls(val)
                q_nodes.append(parent.left)

            if not q_vals:
                break
            val = q_vals.popleft()
            if val is not None:
                parent.right = cls(val)
                q_nodes.append(parent.right)

        return root

    @classmethod
    def from_string(cls, vals):
        try:
            vals = loads(vals)
        except (ValueError, TypeError):
            raise ValueError('vals is not a json string representing an array of values')

        return cls.from_iterable(vals)

    @classmethod
    def make_random(cls, size=100, duplicate=False, binary_search=False):
        """Make a tree of random structure and value

        :param int size: number of nodes in the tree
        :param bool duplicate: whether allow nodes with the same value or not
        :param bool binary_search: whether return a binary search tree or simply a binary tree
        :return TreeNode:
        """
        size = int(size)
        if binary_search:
            if duplicate:
                raise ValueError('a binary search tree does not contain duplicate nodes')
            vals = [0] * size  # just a placeholder array
        else:
            vals = randints(size, unique=not duplicate, max_num=size - 1)

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

        if node:
            if binary_search:
                def _repl_val(node):
                    node.val = next(cnt)

                cnt = count()
                node.traverse_map(_repl_val, cls.INORDER)

        return node


class ListNode(BaseListNode, SerializableDataStructure):
    def __iter__(self):
        return self._gen()

    def __eq__(self, o):
        while self and o:
            if self.val != o.val:
                return False
            self = self.next
            o = o.next
        return self is o is None

    def end(self):
        """
        :return ListNode: last node in the list
        """
        while self.next:
            self = self.next
        return self

    @classmethod
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

    def flatten(self):
        return [list(self)]
