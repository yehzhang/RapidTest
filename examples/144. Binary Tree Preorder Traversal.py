from rapidtest import Test, Case, TreeNode
from solutions.binary_tree_preorder_traversal import Solution

with Test(Solution) as test:
    Case(TreeNode.from_string('[1,null,2,3]'), result=[1, 2, 3])
    Case(TreeNode.from_string('[]'), result=[])
    Case(TreeNode.from_string('[1]'), result=[1])
    Case(TreeNode.from_string('[1,2]'), result=[1, 2])
    Case(TreeNode.from_string('[1,2]'), result=[1, 2])
    Case(TreeNode.from_string(
        '[1,2,null,4,5,null,6,2,null,6,8,4,null,1,2,4,null,6,8,0,9,null,7,5,4,null,3,null,2,3]'),
        result=[1, 2, 4, 6, 6, 1, 0, 3, 9, 2, 7, 8, 4, 5, 4, 5, 2, 4, 6, 3, 8, 2])
