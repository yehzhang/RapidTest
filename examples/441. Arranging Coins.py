from Solution import Solution
from rapidtest import Test, Case

with Test(Solution) as test:
    @test
    def g(i):
        rows = 0
        coins = i
        while coins >= rows:
            coins -= rows
            rows += 1
        return Case(i, result=rows - 1)
