from rapidtest import Test, Case, randints, randstr, Result, unordered
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java', post_proc=unordered) as t:
    Case('word', result=['word', '1ord', 'w1rd', 'wo1d', 'wor1', '2rd', 'w2d', 'wo2', '1o1d', '1or1', 'w1r1', '1o2', '2r1', '3d', 'w3', '4'])
    Case('', result=[''])
    Case('a', result=['a', '1'])
    Case('1', result=['1', '1'])
