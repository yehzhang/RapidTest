from Solution import Solution
from rapidtest import Test, Case, Tree

with Test(Solution) as test:
    Case([], [], result=None)
    Case([1], [1], result=TreeNode.from_iterable([1]))
    Case([1, 2], [2, 1], result=TreeNode.from_iterable([1, None, 2]))
    Case([1, 2], [1, 2], result=TreeNode.from_iterable([2, 1]))
    Case([2, 1], [2, 1], result=TreeNode.from_iterable([1, 2]))
    Case([2, 1], [1, 2], result=TreeNode.from_iterable([2, None, 1]))


    @test
    def r(i):
        tree = Tree.make_random(100)
        return Case(tree.inorder(), tree.postorder(), result=tree.root)
