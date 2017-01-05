from __future__ import print_function

from random import randint

from rapidtest import MAX_INT, MIN_INT, Test, Case

with Test('./solutions/PalindromeNumber.java') as test:
    Case(0, result=True)
    Case(1, result=True)
    Case(121, result=True)
    Case(11, result=True)
    Case(111, result=True)
    Case(10, result=False)
    Case(100, result=False)
    Case(200, result=False)
    Case(300, result=False)
    Case(-1, result=False)
    Case(MIN_INT, result=False)
    Case(MAX_INT, result=False)


    @test(500)
    def range(i):
        return Case(i, result=_is_palindrome(i))


    @test(500)
    def random(i):
        x = randint(0, MAX_INT)
        return Case(x, result=_is_palindrome(x))


    @test(500)
    def negative(i):
        return Case(-i - 1, result=False)


    @test(1000)
    def all_palindromes(i):
        while True:
            p = next(_gen)
            if p and not (len(p) != 1 and p.startswith('0')):
                return Case(int(p), result=True)


    def _is_palindrome(x):
        s = str(x)
        return s == s[::-1]


    def _gen_pals(max_length):
        assert max_length >= 0
        if max_length <= 1:
            yield ''
            if max_length == 1:
                for c in ALPHABET:
                    yield c
        else:
            for pal in _gen_pals(max_length - 1):
                yield pal
                if len(pal) == max_length - 2:
                    for c in ALPHABET:
                        yield c + pal + c


    ALPHABET = '0123456789'

    _gen = _gen_pals(9)  # fits in int
