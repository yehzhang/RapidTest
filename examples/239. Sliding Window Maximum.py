from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case([1], 1, result=[1])
    Case([1, 2, 3, 2, 1], 1, result=[1, 2, 3, 2, 1])
    Case([1, 2, 3, 2, 1], 5, result=[3])
    Case([3, 2, 1, 0, 1], 5, result=[3])
    Case([1, 0, 1, 2, 3], 5, result=[3])
    Case([1, 3, -1, -3, 5, 3, 6, 7], 3, result=[3, 3, 5, 5, 6, 7])
    Case([-1, 0, -1, -2, -3], 5, result=[0])

    @t
    def r(i):
        n = randint(1, i + 1)
        nums = randints(n)
        k = randint(1, n)
        maxes = [max(nums[i:i+k]) for i in range(n - k + 1)]
        return Case(nums, k, result=maxes)
