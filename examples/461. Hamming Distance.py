from __future__ import print_function

from rapidtest import Test, Case
from solutions.hamming_distance import Solution

with Test(Solution) as test:
    Case([4, 14, 2], result=6)
    Case(int('01100000', 2), int('01001010', 2), result=3)
