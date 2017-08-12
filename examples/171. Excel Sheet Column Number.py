from rapidtest import Test, Case
from itertools import combinations, chain
from random import randint

with Test('Solution.java') as t:
    Case('A', result=1)
    Case('B', result=2)
    Case('C', result=3)
    Case('X', result=24)
    Case('Y', result=25)
    Case('Z', result=26)
    Case('AA', result=27)
    Case('AB', result=28)
    Case('AC', result=29)
    Case('AZ', result=52)
    Case('BA', result=53)
    Case('ZZ', result=702)
    Case('AAA', result=703)
    Case('AAB', result=704)
