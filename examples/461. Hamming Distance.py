from __future__ import print_function

from rapidtest import Test, Case
from solutions.hamming_distance import Solution

with Test(Solution) as test:
    Case(1, 4, result=2)
    Case(int('01100000', 2), int('01001010', 2), result=3)
