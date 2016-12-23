class Solution(object):
    def findDuplicates(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """
        res = []

        for num in nums or []:
            num = abs(num)
            i = num - 1
            if nums[i] < 0:
                res.append(num)
            else:
                nums[i] *= -1

        return res
