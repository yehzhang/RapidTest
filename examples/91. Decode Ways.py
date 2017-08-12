from rapidtest import Test, Case
from itertools import combinations, chain
from random import randint

with Test('Solution.java') as t:
    Case('12', result=2)
    Case('1', result=1)
    Case('26', result=2)
    Case('27', result=1)
    Case('227', result=2)
    Case('272', result=1)
    Case('722', result=2)
    Case('222', result=3)
    Case('7264', result=2)
    Case('01', result=0)
    Case('1001', result=0)
