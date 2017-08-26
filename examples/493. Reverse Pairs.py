from rapidtest import Test, Case, randints, randstr, Result, unordered
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case([], result=0)
    Case([0, 0, 0, 0, 0], result=0)
    Case([0, 0, 0, 0, 1], result=0)
    Case([0, 0, 0, 1, 0], result=1)
    Case([1, 0, 0, 0, 0], result=4)
    Case([1, 1, 0, 0, 0], result=6)
    Case([1, 0, 0, 0, 1], result=3)
    Case([0, 1, 1, 0, 0], result=4)
    Case([0, 1, 0, 1, 0], result=3)
    Case([1, 3, 2, 3, 1], result=2)
    Case([2, 4, 3, 5, 1], result=3)
    Case([1, 1, 1, 1, 1, 1, 0], result=6)
    Case([8, 9, 8, 7, 8, 5, 4], result=1)
    Case([6, 9, 8, 7, 5, 5, 4], result=1)
    Case([1, 3, 1, 1, 1, 1, 1], result=5)

    @t
    def r(i):
        length = randint(1, 20)
        ints = randints(length, max_num=9, min_num=1)
        count = [ints[i] > ints[j] * 2 for i in range(0, length) for j in range(i + 1, length)].count(True)
        return Case(ints, result=count)
