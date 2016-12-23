# Definition for a  binary tree node
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class BSTIterator(object):
    def __init__(self, root):
        """
        :type root: TreeNode
        """
        self.g = self._gen(root)
        self._next = None

    def _gen(self, root):
        if root:
            for val in self._gen(root.left):
                yield val
            yield root.val
            for val in self._gen(root.right):
                yield val

    def hasNext(self):
        """
        :rtype: bool
        """
        if self._next is None:
            try:
                self._next = next(self.g)
            except StopIteration:
                return False
        return True

    def next(self):
        """
        :rtype: int
        """
        self.hasNext()
        next = self._next
        self._next = None
        return next

# Your BSTIterator will be called like this:
# i, v = BSTIterator(root), []
# while i.hasNext(): v.append(i.next())
