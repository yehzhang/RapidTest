from random import sample

from Solution import Solution
from rapidtest import Test, Case

with Test(Solution) as test:
    Case([0, 0], 0, result=[1, 2])
    Case([2, 3, 6, 10, 17], 9, result=[2, 3])
    Case([2, 3, 6, 10, 17], 19, result=[1, 5])
    Case([2, 3, 6, 10, 17], 27, result=[4, 5])
    Case([2, 3, 6, 10, 17], 13, result=[2, 4])

    fibx = [0, 1]
    for _ in range(43):  # in case singed int overflows
        fibx.append(fibx[-1] + fibx[-2] + 1)


    @test
    def fibs(i):
        i_l, i_r = sorted(sample(range(len(fibx)), 2))
        return Case(fibx, fibx[i_l] + fibx[i_r], result=[i_l + 1, i_r + 1])
