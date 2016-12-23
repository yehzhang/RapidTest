from math import sqrt


class Solution(object):
    def arrangeCoins(self, n):
        """
        :type n: int
        :rtype: int
        """
        x = int(sqrt(n * 2))
        if x * (x + 1) // 2 <= n:
            return x
        return x - 1
