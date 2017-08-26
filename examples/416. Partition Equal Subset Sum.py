from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case([1, 5, 11, 5], result=True)
    Case([1, 2, 3, 5], result=False)
    Case([2], result=False)
    Case([3], result=False)
    Case([3, 3], result=True)
    Case([2, 1, 1], result=True)
    Case([2, 2], result=True)
    Case([2, 4], result=False)
    Case([2, 1, 1, 2], result=True)
