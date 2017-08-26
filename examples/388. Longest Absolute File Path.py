from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case('', result=0)
    Case('dir', result=0)
    Case('dir\na', result=0)
    Case('dir\na\nb', result=0)
    Case('dir\na.b', result=len('a.b'))
    Case('dir\n\ta.b', result=len('dir/a.b'))
    Case('dir\n\ta\n\t\ta.b', result=len('dir/a/a.b'))
    Case('dir\n\ta\n\ta.b', result=len('dir/a.b'))
    Case('dir\na\n\ta.b', result=len('a/a.b'))
    Case('dir\na\nb\nc\nd\nasdfasd\nas\n\ta.b\nasdf', result=len('as/a.b'))
    Case('dir\n\ta.b', result=len('dir/a.b'))

    # dir
    #     subdir1
    #     subdir2
    #         file.ext
    Case('dir\n\tsubdir1\n\tsubdir2\n\t\tfile.ext',
         result=len('dir/subdir2/file.ext'))

    # dir
    #     subdir1
    #         file1.ext
    #         subsubdir1
    #     subdir2
    #         subsubdir2
    #             file2.ext
    Case('dir\n\tsubdir1\n\t\tfile1.ext\n\t\tsubsubdir1\n\tsubdir2\n\t\tsubsubdir2\n\t\t\tfile2.ext',
         result=len('dir/subdir2/subsubdir2/file2.ext'))

    # dir
    #     a
    #         aa
    #             aaa
    #                 file1.txt
    #     aaaaaaaaaaaaaaaaaaaaa
    #         file2.txt
    Case('dir\n\ta\t\taa\t\t\taaa\t\t\t\tfile1.txt\n\taaaaaaaaaaaaaaaaaaaaa\n\t\tfile2.txt',
         result=len('dir/aaaaaaaaaaaaaaaaaaaaa/file2.txt'))

