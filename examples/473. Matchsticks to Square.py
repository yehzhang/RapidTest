from __future__ import print_function

from rapidtest import Test, Case, TreeNode, memo, randints, MAX_INT, MIN_INT, ListNode, randbool, unordered
from Solution import Solution
from random import sample, randint, shuffle
from itertools import product


with Test(Solution) as test:
    Case([1,1,2,2,2], result=True)
    Case([3,3,3,3,4], result=False)
    Case([1,1,1,1], result=True)
    Case([1,1,1], result=False)
    Case([1,2,1], result=False)
    Case([2,2], result=False)
    Case([4], result=False)
    Case([10,20,10,40,10,15,10,25,20], result=True)
    Case([2,2,2,2,2,6], result=False)
    Case([5,5,5,5,16,4,4,4,4,4,3,3,3,3,4], result=False)
