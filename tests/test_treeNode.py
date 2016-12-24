from unittest import TestCase

from rapidtest import TreeNode, randints


class TestTreeNode(TestCase):
    def test_from_iterable(self):
        root = TreeNode.from_iterable([])
        self.assertIsNone(root)

        for i in range(1, 100):
            vals = randints(i)
            root = TreeNode.from_iterable(vals)
            vals2 = root.flatten()
            self.assertEqual(vals, vals2)

    def test_make_random(self):
        root = TreeNode.make_random(0)
        self.assertIsNone(root)

        for i in range(1, 100):
            root = TreeNode.make_random(i)
            vals = root.flatten()
            root2 = TreeNode.from_iterable(vals)
            self.assertEqual(root, root2)

        root = TreeNode.make_random(0, binary_search=True)
        self.assertIsNone(root)

        for i in range(1, 100):
            root = TreeNode.make_random(i, binary_search=True)

            inorder = root.inorder()
            self.assertEqual(inorder, sorted(inorder))

            vals = root.flatten()
            root2 = TreeNode.from_iterable(vals)
            self.assertEqual(root, root2)
