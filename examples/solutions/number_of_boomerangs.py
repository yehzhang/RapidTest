from collections import defaultdict


class Solution(object):
    def numberOfBoomerangs(self, points):
        """
        :type points: List[List[int]]
        :rtype: int
        """
        total = 0
        dists = defaultdict(lambda: defaultdict(int))

        for i, (x, y) in enumerate(points):
            pivot = x, y
            for x1, y1 in points[i + 1:]:
                dist = (x - x1) ** 2 + (y - y1) ** 2
                dists[pivot][dist] += 1
                dists[(x1, y1)][dist] += 1
            pivot_dists = dists.pop(pivot, {})
            for dist in pivot_dists.values():
                total += dist * (dist - 1)

        return total
