from random import randint

from rapidtest import Test, Case
from solutions.plus_one import Solution

with Test(Solution) as test:
    Case([1], result=[2])
    Case([9], result=[1, 0])
    Case([9, 9], result=[1, 0, 0])
    Case([1, 1], result=[1, 2])
    Case([0], result=[1])
    Case([9, 9, 9, 9, 9, 9], result=[1, 0, 0, 0, 0, 0, 0])


    @test
    def large_nums(i):
        num = randint(2147483648, 10000000000000000)
        digits = [int(d) for d in str(num)]
        res = [int(d) for d in str(num + 1)]
        return Case(digits, result=res)
