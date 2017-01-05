# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution(object):
    def lowestCommonAncestor(self, root, p, q):
        """
        :type root: TreeNode
        :type p: TreeNode
        :type q: TreeNode
        :rtype: TreeNode
        """
        seen = set()

        node = root
        while node:
            seen.add(node.val)
            if node.val == p.val:
                break
            node = node.left if p.val < node.val else node.right

        if node is None:
            return None

        r_node = root
        mark = None
        while r_node:
            if r_node.val in seen:
                mark = r_node
            if r_node.val == q.val:
                break
            r_node = r_node.left if q.val < r_node.val else r_node.right

        return r_node and mark
