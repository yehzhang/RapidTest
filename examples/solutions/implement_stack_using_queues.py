from collections import deque


class Stack(object):
    def __init__(self):
        """
        initialize your data structure here.
        """
        self.q = deque()

    def push(self, x):
        """
        :type x: int
        :rtype: nothing
        """
        q = deque([x])
        q.extend(self.q)
        self.q = q

    def pop(self):
        """
        :rtype: nothing
        """
        return self.q.popleft()

    def top(self):
        """
        :rtype: int
        """
        return self.q[0]

    def empty(self):
        """
        :rtype: bool
        """
        return not self.q
