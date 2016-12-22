from random import randint

from Solution import Solution
from rapidtest import Test, Case, randints, MAX_INT

with Test(Solution) as test:
    Case([], result=0)
    Case([0], result=0)
    Case([1], result=1)
    Case([10], result=1)
    Case([0, 0], result=0)
    Case([0, 1], result=1)
    Case([0, 1, 2], result=1)
    Case([1, 2, 2], result=2)
    Case([1, 2, 2, 3], result=2)
    Case([2, 2, 3, 3], result=2)
    Case([2, 2, 3, 3, 4], result=3)


    @test
    def r(i):
        num_cits = randint(0, i)
        citations = randints(count=num_cits, max_num=num_cits * 2)
        citations.sort()

        count = 0
        min_cites = MAX_INT
        for citation in reversed(citations):
            min_cites = min(citation, min_cites)
            count += 1
            if count > min_cites:
                count -= 1
                break

        return Case(citations, result=count)
