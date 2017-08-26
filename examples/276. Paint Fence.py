from rapidtest import Test, Case, randints, randstr, Result, unordered
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case(20, 10, result=2078522884)
    Case(20, 0, result=0)
    Case(0, 1, result=0)
    Case(1, 1, result=1)
    Case(1, 100, result=100)
    Case(2, 100, result=10000)
    Case(2, 1, result=1)
    Case(3, 1, result=0)
    Case(4, 2, result=10)
