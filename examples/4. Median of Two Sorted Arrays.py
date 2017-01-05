from rapidtest import Test, Case, randints
from solutions.median_of_two_sorted_arrays import Solution

def do_test(target):
    with Test(target) as test:
        Case([1, 3], [2], result=2.0)
        Case([1, 2], [3, 4], result=2.5)

        @test
        def random_numbers(i):
            """
            :param int i: number of times this function is called starting from 0
            :return Case:
            """
            nums1 = sorted(randints(count=i, max_num=i * 100))
            nums2 = sorted(randints(count=max(i, 1), max_num=i * 100))
            result = float(median(nums1 + nums2))
            return Case(nums1, nums2, result=result)

        def median(nums):
            if not nums:
                raise ValueError
            nums = sorted(nums)
            if len(nums) % 2 == 0:
                return float(nums[int(len(nums) / 2)] + nums[int(len(nums) / 2) - 1]) / 2
            return nums[int(len(nums) / 2)]

do_test('./solutions/MedianOfTwoSortedArrays.java')
do_test(Solution)
