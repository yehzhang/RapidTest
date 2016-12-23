class Solution(object):
    def canJump(self, nums):
        """
        :type nums: List[int]
        :rtype: bool
        """
        if not nums:
            return True

        jump = nums[0]
        for num in nums[1:]:
            if jump == 0:
                return False
            jump = max(jump - 1, num)

        return True
