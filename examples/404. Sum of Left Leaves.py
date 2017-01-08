from __future__ import print_function

from rapidtest import MAX_INT, Test, Case, TreeNode, randints

with Test('./solutions/SumOfLeftLeaves.java') as test:
    Case(TreeNode.from_iterable([0]), result=0)
    Case(TreeNode.from_iterable([10]), result=0)
    Case(TreeNode.from_iterable([]), result=0)
    Case(TreeNode.from_iterable([1, None, 2]), result=0)
    Case(TreeNode.from_iterable([1, 2, 3]), result=2)
    Case(TreeNode.from_iterable([1, MAX_INT, 3]), result=MAX_INT)
    Case(TreeNode.from_iterable([1, 2, 3, 4, 5]), result=4)


    @test
    def random_complete_tree(i):
        vals = randints(i + 2, max_num=i * 100)
        root = TreeNode.from_iterable(vals)
        i_first_leaf = int(len(vals) / 2)
        i_last_left_left = len(vals) - len(vals) % 2 - 1
        result = sum(vals[i_last_left_left:i_first_leaf - 1:-2])
        return Case(root, result=result)
