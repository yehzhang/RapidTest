from __future__ import print_function

from rapidtest import Test, Case, TreeNode, memo, randints, MAX_INT, MIN_INT, ListNode, randbool, unordered
from Solution import Solution
from random import sample, randint, shuffle
from itertools import product


with Test(Solution, post_proc=unordered) as test:
    Case([], result=[])
    Case([1], result=[])
    Case([1,2], result=[])
    Case([1,2,1], result=[1])
    Case([2,2,1,1], result=[1,2])

    @test
    def r(i):
        cnt_twice = randint(0, i)
        cnt_nums = cnt_twice + i
        nums = randints(i, unique=True, max_num=cnt_nums, min_num=1)
        twice_nums = nums[:cnt_twice]
        once_nums = nums[cnt_twice:]
        nums = twice_nums * 2 + once_nums
        shuffle(nums)
        return Case(nums, result=twice_nums)
