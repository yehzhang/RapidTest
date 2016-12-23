class Solution(object):
    def getRow(self, rowIndex):
        """
        :type rowIndex: int
        :rtype: List[int]
        """
        if rowIndex < 0:
            return []

        last_row = [1]
        for i in range(rowIndex):
            row = [1]
            row.extend(n1 + n2 for n1, n2 in zip(last_row, last_row[1:]))
            row.append(1)
            last_row = row

        return last_row
