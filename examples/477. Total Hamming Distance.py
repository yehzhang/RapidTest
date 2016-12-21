from __future__ import print_function

from rapidtest import Test, Case, TreeNode, memo, randints, MAX_INT, MIN_INT, ListNode, randbool, unordered
from Solution import Solution
from random import sample, randint, shuffle
from itertools import product


with Test(Solution) as test:
    Case([4, 14, 2], result=6)

    @test
    def r(i):
        def hammingDistance(x, y):
            diff = x ^ y
            return sum((diff >> i) & 1 for i in range(32))

        def make():
            return int(''.join(map(str, randints(count=32, max_num=1))), 2)

        nums = [make() for _ in range(i)]
        res = 0
        for i, num in enumerate(nums):
            for j in range(i):
                num2 = nums[j]
                res += hammingDistance(num, num2)
        return Case(nums, result=res)
