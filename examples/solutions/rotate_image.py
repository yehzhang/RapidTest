class Solution(object):
    def rotate(self, matrix):
        """
        :type m: List[List[int]]
        :rtype: void Do not return anything, modify matrix in-place instead.
        """
        m = matrix
        side = len(m)
        max_i = side - 1
        for i in range(side // 2):
            y = i
            for j in range(max_i - i * 2):
                x = i + j
                m[y][x], m[x][max_i - y], m[max_i - y][max_i - x], m[max_i - x][y] = \
                    m[max_i - x][y], m[y][x], m[x][max_i - y], m[max_i - y][max_i - x]
