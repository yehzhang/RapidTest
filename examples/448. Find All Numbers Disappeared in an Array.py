from __future__ import print_function

from random import randint, shuffle

from rapidtest import Test, Case, randints, unordered
from solutions.find_all_numbers_disappeared_in_an_array import Solution

with Test(Solution, post_proc=unordered) as test:
    Case([], result=[])
    Case([1], result=[])
    Case([1, 2], result=[])
    Case([1, 2, 1], result=[3])
    Case([2, 2, 1, 1], result=[3, 4])


    @test
    def r(i):
        cnt_twice = randint(0, i)
        cnt_nums = cnt_twice + i
        nums = randints(i, unique=True, max_num=cnt_nums, min_num=1)
        twice_nums = nums[:cnt_twice]
        once_nums = nums[cnt_twice:]
        nums = twice_nums * 2 + once_nums
        shuffle(nums)
        missing = list(set(range(1, cnt_nums + 1)) - set(nums))
        return Case(nums, result=missing)
