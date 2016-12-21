from __future__ import print_function

from rapidtest import Test, Case, TreeNode, memo, randints, MAX_INT, MIN_INT, ListNode, randbool, unordered
from Solution import Solution
from random import sample, randint, shuffle
from itertools import product


with Test(Solution) as test:
    Case([4, 14, 2], result=6)
    Case(int('01100000', 2), int('01001010', 2), result=3)
