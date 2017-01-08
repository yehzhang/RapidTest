from importlib import import_module

from rapidtest.utils import Reprable


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


class Node(Reprable):
    NULL = '#'

    def __str__(self):
        raise NotImplementedError


class TreeNode(Node):
    NAME = 'TreeNode'

    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

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


class ListNode(Node):
    NAME = 'ListNode'

    def __init__(self, x):
        self.val = x
        self.next = None

    def __str__(self):
        vals = list(self._gen())
        vals.append(self.NULL)
        return '{}'.format('->'.join(map(str, vals)))

    def _gen(self):
        """
        :return Iterator[T]: generator that traverses self
        """
        while self:
            yield self.val
            self = self.next
