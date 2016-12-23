import heapq


class Solution(object):
    def thirdMax(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        heap = []

        for num in nums:
            if num not in heap:
                (heapq.heappushpop if len(heap) >= 3 else heapq.heappush)(heap, num)

        heap.sort()
        return heap[-3 if len(heap) >= 3 else -1]
