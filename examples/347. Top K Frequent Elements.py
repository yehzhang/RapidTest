from random import randint, shuffle

from rapidtest import Test, Case, randints, MAX_INT, MIN_INT
from solutions.top_k_frequent_elements import Solution

with Test(Solution) as test:
    Case([2], 1, result=[2])
    Case([2, 2], 1, result=[2])
    Case([1, 2, 2], 1, result=[2])
    Case([1, 2, 2, 3, 4], 1, result=[2])
    Case([4, 1, 2, 2, 3, 4, 4], 1, result=[4])
    Case([1, 1, 1, 2, 2, 3], 2, result=[1, 2])
    Case([4, 1, 2, 2, 3, 2, 4, 4, 4], 2, result=[4, 2])


    @test
    def r(i):
        cnt_nums = randint(1, 50)
        k = randint(1, cnt_nums)
        items = randints(cnt_nums, unique=True, min_num=MIN_INT, max_num=MAX_INT)
        num_repeats = randints(cnt_nums, unique=True, min_num=1, max_num=cnt_nums + 1)
        num_repeats.sort(reverse=True)
        nums = sum(([item] * repeat for item, repeat in zip(items, num_repeats)), [])
        shuffle(nums)
        return Case(nums, k, result=items[:k])
