from Solution import Solution
from rapidtest import Test, Case, memo

with Test(Solution) as test:
    @memo
    def gen_pascal_triangle(num_rows):
        if num_rows <= 0:
            return []
        if num_rows == 1:
            return [[1]]
        rows = gen_pascal_triangle(num_rows - 1)
        last_row = rows[-1]
        this_row = [1]
        this_row.extend(n1 + n2 for n1, n2 in zip(last_row, last_row[1:]))
        this_row.append(1)
        rows.append(this_row)
        return rows

    @test
    def g(i):
        result = gen_pascal_triangle(i)
        return Case(i, result=result)
