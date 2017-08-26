from rapidtest import Test, Case, randints, randstr, Result, unordered
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java', post_proc=unordered) as t:
    Case([
        'abcd',
        'bnrt',
        'crmy',
        'dtye'
    ], result=True)
    Case([
        'abcd',
        'bnrt',
        'crm',
        'dt'
    ], result=True)
    Case([
        'ball',
        'area',
        'read',
        'lady'
    ], result=False)
    Case([
        'b',
    ], result=True)
    Case([
        'ba',
    ], result=False)
    Case([
        'b',
        'a',
    ], result=False)
    Case([
        'ba',
        'b',
    ], result=False)
    Case([
        'ba',
        'a',
    ], result=True)
    Case([
        'ba',
        'ac',
    ], result=True)
