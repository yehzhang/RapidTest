from rapidtest import Test, Case, randints
from itertools import combinations, chain, permutations
from random import randint

with Test('Solution.java') as t:
    Case(12, result=21)
    Case(21, result=-1)
    Case(1234, result=1243)
    Case(4321, result=-1)
    Case(0, result=-1)
    Case(123, result=132)
    Case(132, result=213)
    Case(213, result=231)
    Case(231, result=312)
    Case(312, result=321)
    Case(321, result=-1)

    Case(331, result=-1)
    Case(313, result=331)
    Case(2331, result=3123)
    Case(1999999999, result=-1)
