from unittest import TestCase

from rapidtest import randints
from rapidtest.data_structures import SuperTreeNode


class TestTreeNode(TestCase):
    def test_from_iterable(self):
        root = SuperTreeNode.from_iterable([])
        self.assertIsNone(root)

        for i in range(1, 100):
            vals = randints(i)
            root = SuperTreeNode.from_iterable(vals)
            vals2 = root.flatten()
            self.assertEqual(vals, vals2)

    def test_make_random(self):
        root = SuperTreeNode.make_random(0)
        self.assertIsNone(root)

        for i in range(1, 100):
            root = SuperTreeNode.make_random(i)
            vals = root.flatten()
            root2 = SuperTreeNode.from_iterable(vals)
            self.assertEqual(i, len(vals) - vals.count(None))
            self.assertEqual(root, root2)

        root = SuperTreeNode.make_random(0, binary_search=True)
        self.assertIsNone(root)

        for i in range(1, 100):
            root = SuperTreeNode.make_random(i, binary_search=True)

            inorder = root.inorder()
            self.assertEqual(i, len(inorder))
            self.assertEqual(inorder, sorted(inorder))

            vals = root.flatten()
            self.assertEqual(i, len(vals) - vals.count(None))
            root2 = SuperTreeNode.from_iterable(vals)
            self.assertEqual(root, root2)
