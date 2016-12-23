from rapidtest import Test, Case, TreeNode
from solutions.lowest_common_ancestor_of_a_binary_search_tree import Solution

with Test(Solution) as test:
    root = TreeNode.from_iterable([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    Case(root, TreeNode(2), TreeNode(4), result=TreeNode(2))
    Case(root, TreeNode(4), TreeNode(2), result=TreeNode(2))
    Case(root, TreeNode(2), TreeNode(8), result=TreeNode(6))
    Case(root, TreeNode(8), TreeNode(2), result=TreeNode(6))
    Case(root, TreeNode(3), TreeNode(7), result=TreeNode(6))
    Case(root, TreeNode(0), TreeNode(4), result=TreeNode(2))
    Case(root, TreeNode(0), TreeNode(5), result=TreeNode(2))
    Case(root, TreeNode(2), TreeNode(6), result=TreeNode(6))
    Case(root, TreeNode(6), TreeNode(2), result=TreeNode(6))
    Case(root, TreeNode(6), TreeNode(2), result=TreeNode(6))
    Case(root, TreeNode(0), TreeNode(0), result=TreeNode(0))


    @test
    def greater_children(i):
        return Case(TreeNode.from_iterable([i, None, i + 1]), TreeNode(i), TreeNode(i + 1),
                    result=TreeNode(i))


    @test
    def smaller_children(i):
        return Case(TreeNode.from_iterable([i, i - 1]), TreeNode(i), TreeNode(i - 1),
                    result=TreeNode(i))
