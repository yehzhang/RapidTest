from unittest import TestCase

from rapidtest import randints
from rapidtest.data_structures import ListNode


class TestSuperListNode(TestCase):
    def test_end(self):
        for i in range(1, 100):
            vals = randints(i)
            root = ListNode.from_iterable(vals)
            vals = list(root)
            self.assertEqual(root.end().val, vals[-1])

    def test_from_iterable(self):
        root = ListNode.from_iterable([])
        self.assertIsNone(root)

        for i in range(1, 100):
            vals = randints(i)
            root = ListNode.from_iterable(vals)
            vals2 = list(root)
            self.assertEqual(vals, vals2)
