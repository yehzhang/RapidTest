from __future__ import print_function

from rapidtest import Result, Test, Case, randints
from solutions.find_median_from_data_stream import MedianFinder

with Test(MedianFinder, operation=True) as test:
    Case('addNum', [1],
         'findMedian', Result(1),
         'addNum', [1],
         'findMedian', Result(1.0),
         'addNum', [2],
         'findMedian', Result(1),
         'addNum', [2],
         'findMedian', Result(1.5),
         'addNum', [0],
         'findMedian', Result(1))


    @test
    def r(i):
        ops = []
        nums = randints(max(1, i), max_num=75)
        tmp_nums = []
        for num in nums:
            tmp_nums.append(num)
            tmp_nums.sort()
            if len(tmp_nums) % 2 == 1:
                median = tmp_nums[len(tmp_nums) // 2]
            else:
                median = float(tmp_nums[len(tmp_nums) // 2] + tmp_nums[len(tmp_nums) // 2 - 1]) / 2
            ops.extend(['addNum', [num], 'findMedian', Result(median)])
        return Case(*ops)
