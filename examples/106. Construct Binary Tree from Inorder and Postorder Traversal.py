from rapidtest import Test, Case, TreeNode
from solutions.construct_binary_tree_from_inorder_and_postorder_traversal import Solution

with Test(Solution) as test:
    Case([], [], result=None)
    Case([1], [1], result=TreeNode.from_iterable([1]))
    Case([1, 2], [2, 1], result=TreeNode.from_iterable([1, None, 2]))
    Case([1, 2], [1, 2], result=TreeNode.from_iterable([2, 1]))
    Case([2, 1], [2, 1], result=TreeNode.from_iterable([1, 2]))
    Case([2, 1], [1, 2], result=TreeNode.from_iterable([2, None, 1]))


    @test
    def r(i):
        root = TreeNode.make_random(max(1, i))
        return Case(root.inorder(), root.postorder(), result=root)
