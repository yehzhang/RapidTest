class LinkedList:
    tail = None
    root = None

    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None

    def remove(self):
        if self is not LinkedList.root:
            if self.next:
                self.next.prev = self.prev
            if self.prev:
                self.prev.next = self.next
            if self is LinkedList.tail:
                LinkedList.tail = self.prev or self.root

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


class LRUCache(object):
    def __init__(self, capacity):
        """
        :type capacity: int
        """
        self.capacity = capacity
        self.d = {}
        self.root = LinkedList(None)
        LinkedList.root = self.root
        LinkedList.tail = self.root

    def get(self, key):
        """
        :rtype: int
        """
        if key in self.d:
            node = self.d[key]
            self._use(node)
            _, val = node.val

        else:
            val = -1

        return val

    def set(self, key, value):
        """
        :type key: int
        :type value: int
        :rtype: nothing
        """
        if key in self.d:
            node = self.d[key]
            node.val = key, value
            self._use(node)

        else:
            node = self.root.append((key, value))
            self.d[key] = node

            if len(self.d) > self.capacity:
                node = LinkedList.tail
                node.remove()
                key, _ = node.val
                del self.d[key]

    def _use(self, node):
        node.remove()
        node.next = self.root.next
        node.prev = self.root
        if self.root.next:
            self.root.next.prev = node
        self.root.next = node
        if node.prev is LinkedList.tail:
            LinkedList.tail = node
