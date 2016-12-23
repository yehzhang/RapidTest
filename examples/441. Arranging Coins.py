from rapidtest import Test, Case
from solutions.arranging_coins import Solution

with Test(Solution) as test:
    @test
    def g(i):
        rows = 0
        coins = i
        while coins >= rows:
            coins -= rows
            rows += 1
        return Case(i, result=rows - 1)
