class Solution(object):
    def hIndex(self, citations):
        """
        :type citations: List[int]
        :rtype: int
        """
        i_l = 0
        i_r = len(citations) - 1
        h_index = 0

        while i_l <= i_r:
            i_m = (i_l + i_r) // 2
            count = len(citations) - i_m
            citation = citations[i_m]
            if count >= citation:
                h_index = max(citation, h_index)
                i_l = i_m + 1
            else:
                h_index = max(count, h_index)
                i_r = i_m - 1

        return h_index
