from __future__ import print_function

from Solution import Solution
from rapidtest import Test, Case

with Test(Solution) as test:
    Case([], result=True)
    Case([0], result=True)
    Case([0, 1], result=False)
    Case([1, 0], result=True)
    Case([1, 0, 0], result=False)
    Case([2, 0, 0], result=True)
    Case([1, 1, 0], result=True)
    Case([3, 0, 0, 0], result=True)
    Case([2, 0, 0, 10], result=False)
    Case([2, 3, 1, 1, 4], result=True)
    Case([3, 2, 1, 0, 4], result=False)
