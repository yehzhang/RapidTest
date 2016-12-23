from heapq import heappush, heappop


class MedianFinder:
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.l = []
        self.r = []

    def addNum(self, num):
        """
        Adds a num into the data structure.
        :type num: int
        :rtype: void
        """
        if not self.l and not self.r:
            self.r.append(num)
        else:
            median = self.findMedian()
            if num > median:
                heappush(self.r, num)
                if len(self.r) > len(self.l) + 1:
                    r = heappop(self.r)
                    heappush(self.l, -r)
            else:
                heappush(self.l, -num)
                if len(self.l) > len(self.r) + 1:
                    l = -heappop(self.l)
                    heappush(self.r, l)

    def findMedian(self):
        """
        Returns the median of current data stream
        :rtype: float
        """
        if len(self.l) == len(self.r):
            return float(-self.l[0] + self.r[0]) / 2
        return -self.l[0] if len(self.l) > len(self.r) else self.r[0]


        # Your MedianFinder object will be instantiated and called as such:
        # mf = MedianFinder()
        # mf.addNum(1)
        # mf.findMedian()
