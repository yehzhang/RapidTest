from rapidtest import Test, Case, randints
from itertools import combinations, chain, permutations
from random import randint

with Test('Solution.java', in_place=0) as t:
    Case([1, 2, 3, 4], result=[1, 2, 4, 3])
    Case([4, 3, 2, 1], result=[1, 2, 3, 4])
    Case([], result=[])
    Case([1, 2, 3], result=[1, 3, 2])
    Case([1, 3, 2], result=[2, 1, 3])
    Case([2, 1, 3], result=[2, 3, 1])
    Case([2, 3, 1], result=[3, 1, 2])
    Case([3, 1, 2], result=[3, 2, 1])
    Case([3, 2, 1], result=[1, 2, 3])

    Case([3, 3, 1], result=[1, 3, 3])
    Case([3, 1, 3], result=[3, 3, 1])
    Case([2, 3, 3, 1], result=[3, 1, 2, 3])
