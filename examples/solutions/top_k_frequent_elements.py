from collections import Counter


class Solution(object):
    def topKFrequent(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: List[int]
        """
        cnts = sorted(((v, k) for k, v in Counter(nums).items()), reverse=True)[:k]
        return [v for k, v in cnts]
