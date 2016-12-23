class Queue(object):
    def __init__(self):
        """
        initialize your data structure here.
        """
        self.l = []
        self._r = []

    @property
    def r(self):
        if not self._r:
            self._r = self.l[::-1]
            self.l = []
        return self._r

    def push(self, x):
        """
        :type x: int
        :rtype: nothing
        """
        self.l.append(x)

    def pop(self):
        """
        :rtype: nothing
        """
        return self.r.pop()

    def peek(self):
        """
        :rtype: int
        """
        return self.r[-1]

    def empty(self):
        """
        :rtype: bool
        """
        return not self.r
