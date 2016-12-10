from Solution import Solution
from rapidtest import Test, Case, Tree, TreeNode

with Test(Solution) as test:
    root = Tree.make_root([6,2,8,0,4,7,9,None,None,3,5])
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
        return Case(Tree.make_root([i,None,i+1]), TreeNode(i), TreeNode(i + 1), result=TreeNode(i))

    @test
    def smaller_children(i):
        return Case(Tree.make_root([i,i-1]), TreeNode(i), TreeNode(i - 1), result=TreeNode(i))

