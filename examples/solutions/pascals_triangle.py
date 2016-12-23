class Solution(object):
    def generate(self, numRows):
        """
        :type numRows: int
        :rtype: List[List[int]]
        """
        if numRows <= 0:
            return []

        rows = [[1]]
        for i in range(1, numRows):
            last_row = rows[-1]
            row = [1]
            row.extend(n1 + n2 for n1, n2 in zip(last_row, last_row[1:]))
            row.append(1)
            rows.append(row)

        return rows
