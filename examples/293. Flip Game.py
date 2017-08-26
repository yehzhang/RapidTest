from rapidtest import Test, Case, randints, randstr, Result, unordered
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java', post_proc=unordered) as t:
    Case("++++", result=["--++", "+--+", "++--"])
    Case("+++", result=["--+", "+--"])
    Case("++", result=["--"])
    Case("--", result=[])
    Case("+-+", result=[])
    Case("+", result=[])
    Case("", result=[])
    Case("+-+-", result=[])
    Case("+-++-", result=['+----'])
