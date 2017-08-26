from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case('eceba', result=len('ece'))
    Case('abcabcbb', result=len('bcbb'))
    Case('bbbbb', result=len('bbbbb'))
    Case('pwwkew', result=len('pww'))
    Case('', result=len(''))
    Case('a', result=len('a'))
    Case('b', result=len('b'))
    Case('ab', result=len('ab'))
    Case('abc', result=len('ab'))
    Case('abcb', result=len('bcb'))

    @t
    def r(i):
        mid = list('a' * randint(1, i + 1) + 'b' * randint(1, i + 1))
        shuffle(mid)
        mid = ''.join(mid)
        non_repeating = list(set(ascii_lowercase) - set('ab'))
        left = randstr(length=randint(0, len(non_repeating)), unique=True, alphabet=non_repeating)
        right = randstr(length=randint(0, len(non_repeating)), unique=True, alphabet=non_repeating)
        return Case(left + mid + right, result=len(mid))
