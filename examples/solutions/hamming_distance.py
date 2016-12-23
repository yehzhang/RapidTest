class Solution(object):
    def hammingDistance(self, x, y):
        """
        :type x: int
        :type y: int
        :rtype: int
        """
        diff = x ^ y
        return sum((diff >> i) & 1 for i in range(32))
