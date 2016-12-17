from Solution import Solution
from rapidtest import Test, Case

with Test(Solution) as test:
    ans = {
        0: 1,
        1: 10,
        2: 91,
        3: 739,
        4: 5275,
        5: 32491,
        6: 168571,
        7: 712891,
        8: 2345851,
        9: 5611771,
        10: 8877691,
    }

    @test
    def r(i):
        return Case(i, result=ans[min(i, 10)])
