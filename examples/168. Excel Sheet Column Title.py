from rapidtest import Test, Case
from itertools import combinations, chain
from random import randint

with Test('Solution.java') as t:
    Case(1, result='A')
    Case(2, result='B')
    Case(3, result='C')
    Case(24, result='X')
    Case(25, result='Y')
    Case(26, result='Z')
    Case(27, result='AA')
    Case(28, result='AB')
    Case(676, result='YZ')
    Case(702, result='ZZ')
    Case(703, result='AAA')
    Case(704, result='AAB')
