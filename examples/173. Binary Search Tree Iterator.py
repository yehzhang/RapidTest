from __future__ import print_function

from Solution import BSTIterator
from rapidtest import Result, Test, Case, TreeNode

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
    def r(i):
        ops = []
        root = TreeNode.make_random(i, binary_search=True)
        ops.append([root])
        if root:
            for val in root.inorder():
                ops.extend(['hasNext', Result(True), 'next', Result(val)])
        ops.extend(['hasNext', Result(False)])
        return Case(*ops)
