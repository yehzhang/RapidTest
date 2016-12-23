class Solution(object):
    def twoSum(self, numbers, target):
        """
        :type numbers: List[int]
        :type target: int
        :rtype: List[int]
        """
        i_l = 0
        i_r = len(numbers) - 1

        while i_l < i_r:
            sum_pair = numbers[i_l] + numbers[i_r]
            if sum_pair == target:
                return [i_l + 1, i_r + 1]
            if sum_pair < target:
                i_l += 1
            else:
                i_r -= 1
