from rapidtest import Test, Case, randints
from solutions.rotate_image import Solution

with Test(Solution, in_place=0) as test:
    Case([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ], result=[
        [7, 4, 1],
        [8, 5, 2],
        [9, 6, 3],
    ])

    @test
    def r(i):
        matrix = [randints(count=i, max_num=i) for _ in range(i)]
        result = list(zip(*reversed(matrix)))
        return Case(matrix, result=result)
