from __future__ import print_function

from random import randint, shuffle

from rapidtest import Test, Case, randints, unordered
from solutions.find_all_duplicates_in_an_array import Solution

with Test(Solution, post_proc=unordered) as test:
    Case([], result=[])
    Case([1], result=[])
    Case([1, 2], result=[])
    Case([1, 2, 1], result=[1])
    Case([2, 2, 1, 1], result=[1, 2])


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
