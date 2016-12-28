from unittest import TestCase

from rapidtest import randints
from rapidtest.data_structures import SuperListNode


class TestSuperListNode(TestCase):
    def test_end(self):
        for i in range(1, 100):
            root = SuperListNode.make_random(i)
            vals = list(root)
            self.assertEqual(root.end().val, vals[-1])

    def test_from_iterable(self):
        root = SuperListNode.from_iterable([])
        self.assertIsNone(root)

        for i in range(1, 100):
            vals = randints(i)
            root = SuperListNode.from_iterable(vals)
            vals2 = list(root)
            self.assertEqual(vals, vals2)

    def test_make_random(self):
        root = SuperListNode.make_random(0)
        self.assertIsNone(root)

        for i in range(1, 100):
            root = SuperListNode.make_random(i)
            vals = list(root)
            root2 = SuperListNode.from_iterable(vals)
            self.assertEqual(i, len(vals))
            self.assertEqual(root, root2)
