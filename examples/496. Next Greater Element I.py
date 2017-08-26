from rapidtest import Test, Case
from itertools import combinations, chain
from random import randint

with Test('Solution.java') as t:
    Case([1, 2, 3, 4], [1, 2, 3, 4], result=[2, 3, 4, -1])
    Case([4, 3, 2, 1], [4, 3, 2, 1], result=[-1, -1, -1, -1])
    Case([2, 4], [1, 2, 3, 4], result=[3, -1])
    Case([4, 1, 2], [1, 3, 4, 2], result=[-1, 3, -1])
    Case([1, 3, 2, 4], [1, 3, 2, 4], result=[3, 4, 4, -1])
    Case([4, 2, 3, 1], [4, 2, 3, 1], result=[-1, 3, -1, -1])
