class LinkedList:
    tail = None
    root = None

    def __init__(self, val):
        self.val = val
        self.keys = set()
        self.next = None
        self.prev = None

    @property
    def count(self):
        return len(self.keys)

    def remove(self, key):
        self.keys.remove(key)
        if not self.count and self is not LinkedList.root:
            if self.next:
                self.next.prev = self.prev
            if self.prev:
                self.prev.next = self.next
            if self is LinkedList.tail:
                LinkedList.tail = self.prev

    def append(self, val):
        next_node = LinkedList(val)
        next_node.prev = self
        next_node.next = self.next
        if next_node.next:
            next_node.next.prev = next_node
        self.next = next_node
        if self is LinkedList.tail:
            LinkedList.tail = next_node
        return next_node

    def appendleft(self, val):
        prev_node = LinkedList(val)
        prev_node.next = self
        prev_node.prev = self.prev
        if prev_node.prev:
            prev_node.prev.next = prev_node
        self.prev = prev_node
        return prev_node


class AllOne(object):
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.d = {}
        self.root = LinkedList(1)
        LinkedList.tail = self.root
        LinkedList.root = self.root

    def inc(self, key):
        """
        Inserts a new key <Key> with value 1. Or increments an existing key by 1.
        :type key: str
        :rtype: void
        """
        if key in self.d:
            curr_node = self.d[key]
            next_val = curr_node.val + 1
            if curr_node.next and curr_node.next.val == next_val:
                next_node = curr_node.next
            else:
                next_node = curr_node.append(next_val)
            curr_node.remove(key)
        else:
            next_node = self.root

        next_node.keys.add(key)
        self.d[key] = next_node

    def dec(self, key):
        """
        Decrements an existing key by 1. If Key's value is 1, remove it from the data structure.
        :type key: str
        :rtype: void
        """
        if key in self.d:
            curr_node = self.d[key]
            prev_val = curr_node.val - 1
            if curr_node.prev and curr_node.prev.val == prev_val:
                prev_node = curr_node.prev
            elif prev_val > 0:
                prev_node = curr_node.appendleft(prev_val)
            curr_node.remove(key)

            if prev_val == 0:
                del self.d[key]
            else:
                prev_node.keys.add(key)
                self.d[key] = prev_node

    def getMaxKey(self):
        """
        Returns one of the keys with maximal value.
        :rtype: str
        """
        node = self.root.tail
        if node.count == 0:
            return ''
        else:
            return next(iter(node.keys))

    def getMinKey(self):
        """
        Returns one of the keys with Minimal value.
        :rtype: str
        """
        node = self.root if self.root.count else self.root.next
        if not node:
            return ''
        else:
            return next(iter(node.keys))

            # Your AllOne object will be instantiated and called as such:
            # obj = AllOne()
            # obj.inc(key)
            # obj.dec(key)
            # param_3 = obj.getMaxKey()
            # param_4 = obj.getMinKey()
