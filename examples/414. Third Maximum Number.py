from __future__ import print_function

from Solution import Solution
from rapidtest import Test, Case, randints

with Test(Solution) as test:
    Case([1], result=1)
    Case([1, 2], result=2)
    Case([1, 2, 3], result=1)
    Case([2, 2, 3, 1], result=1)


    @test
    def r(i):
        nums = randints(max(1, i))
        res_nums = sorted(set(nums))
        res = res_nums[-3 if len(res_nums) >= 3 else -1]
        return Case(nums, result=res)
