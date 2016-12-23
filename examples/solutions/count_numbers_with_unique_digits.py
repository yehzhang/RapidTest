class Solution(object):
    def countNumbersWithUniqueDigits(self, n):
        """
        :type n: int
        :rtype: int
        """
        cnt = 1
        prod = 9
        for i in range(min(n, 10)):
            cnt += prod
            prod *= 9 - i
        return cnt
