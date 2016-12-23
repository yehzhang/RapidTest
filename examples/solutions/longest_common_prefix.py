class Solution(object):
    def longestCommonPrefix(self, strs):
        """
        :type strs: List[str]
        :rtype: str
        """
        if not strs:
            return ""
        comm = strs[0]
        for s in strs[1:]:
            i = 0
            for i, (c, c2) in enumerate(zip(s, comm)):
                if c != c2:
                    break
            else:
                if s and comm:
                    i += 1
            comm = s[:i]
        return comm
