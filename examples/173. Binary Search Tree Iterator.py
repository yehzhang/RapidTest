from __future__ import print_function

from rapidtest import Result, Test, Case, TreeNode
from solutions.binary_search_tree_iterator import BSTIterator

with Test(BSTIterator, operation=True) as test:
    root = TreeNode.from_iterable([5, 3, 7, 1, 4, 6, 8, None, 2])
    Case([root],
         'hasNext', Result(True),
         'next', Result(1),
         'hasNext', Result(True),
         'next', Result(2),
         'hasNext', Result(True),
         'next', Result(3),
         'hasNext', Result(True),
         'next', Result(4),
         'hasNext', Result(True),
         'next', Result(5),
         'hasNext', Result(True),
         'next', Result(6),
         'hasNext', Result(True),
         'next', Result(7),
         'hasNext', Result(True),
         'next', Result(8),
         'hasNext', Result(False))

    @test
    def random_case(i):
        """
        :param int i: number of times this function is called starting from 0
        :return Case:
        """
        root = TreeNode.make_random(size=i)
        return _make_case(root)

    @test(50)
    def random_case_with_duplicate_nodes(i):
        root = TreeNode.make_random(size=i, duplicate=True)
        return _make_case(root)

    def _make_case(root):
        operations = []

        # Constructor arguments
        operations.append([root])

        # Methods names and asserted results
        if root is not None:
            for val in root.inorder():
                operations.extend(['hasNext', Result(True), 'next', Result(val)])
        operations.extend(['hasNext', Result(False)])

        return Case(*operations)
