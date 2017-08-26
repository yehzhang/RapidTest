from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case('abcabcbb', result=len('abc'))
    Case('bbbbb', result=len('b'))
    Case('pwwkew', result=len('wke'))

    @t
    def r(i):
        mid = randstr(length=min(i, 26), unique=True, alphabet=ascii_lowercase)
        left = randstr(length=randint(0, i), alphabet=mid)
        right = randstr(length=randint(0, i), alphabet=mid)
        return Case(left + mid + right, result=len(mid))
