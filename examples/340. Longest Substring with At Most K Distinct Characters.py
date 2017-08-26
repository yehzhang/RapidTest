from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case('eceba', 2, result=len('ece'))
    Case('abcabcbb', 2, result=len('bcbb'))
    Case('bbbbb', 2, result=len('bbbbb'))
    Case('pwwkew', 2, result=len('pww'))
    Case('',  2,result=len(''))
    Case('a', 2, result=len('a'))
    Case('b', 2, result=len('b'))
    Case('ab', 2, result=len('ab'))
    Case('abc', 2, result=len('ab'))
    Case('abcb', 2, result=len('bcb'))
    Case('abcb', 1, result=len('a'))
    Case('abbcb', 1, result=len('bb'))

    @t
    def r2(i):
        mid = list('a' * randint(1, i + 1) + 'b' * randint(1, i + 1))
        shuffle(mid)
        mid = ''.join(mid)
        non_repeating = list(set(ascii_lowercase) - set('ab'))
        left = randstr(length=randint(0, len(non_repeating)), unique=True, alphabet=non_repeating)
        right = randstr(length=randint(0, len(non_repeating)), unique=True, alphabet=non_repeating)
        return Case(left + mid + right, 2, result=len(mid))

    @t
    def r0(i):
        mid = list('a' * randint(1, i + 1) + 'b' * randint(1, i + 1))
        shuffle(mid)
        mid = ''.join(mid)
        non_repeating = list(set(ascii_lowercase) - set('ab'))
        left = randstr(length=randint(0, len(non_repeating)), unique=True, alphabet=non_repeating)
        right = randstr(length=randint(0, len(non_repeating)), unique=True, alphabet=non_repeating)
        return Case(left + mid + right, 0, result=0)
