from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    Case([0,1,0,2,1,0,1,3,2,1,2,1], result=6)
    Case([0,1,0,2,1,0,1,3,2,1,2,1][::-1], result=6)
    Case([0,1,2,3,4,5,4,3,2,3,4,3,2,1,2,3,2,1,2,1,0], result=9)
    Case([0,1,2,3,4,5,4,3,2,3,4,3,2,1,2,3,2,1,2,1,0][::-1], result=9)
