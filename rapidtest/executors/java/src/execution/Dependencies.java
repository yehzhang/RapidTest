package execution;

import java.io.Serializable;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Stack;

public class Dependencies {
    static abstract class Node<T extends Serializable> implements Json.Serializable {
        @Override
        public boolean isAttributes() {
            return false;
        }

        @Override
        public List<T> getParams() {
            return flatten();
        }

        abstract List<T> flatten();

        @Override
        public String getName() {
            return getClass().getSimpleName();
        }
    }

    public static class TreeNode extends Node<Integer> {
        public TreeNode(int val) {
            this.val = val;
        }

        static TreeNode fromIterable(Integer[] vals) {
            if (vals == null || vals.length == 0) {
                return null;
            }

            int i = 0;
            if (vals[i] == null) {
                throw new IllegalArgumentException("root of tree cannot be null");
            }
            TreeNode root = new TreeNode(vals[i++]);

            Queue<TreeNode> qNodes = new ArrayDeque<>();
            qNodes.offer(root);

            while (i < vals.length && !qNodes.isEmpty()) {
                TreeNode parent = qNodes.poll();
                Integer val = vals[i++];
                if (val != null) {
                    parent.left = new TreeNode(val);
                    qNodes.offer(parent.left);
                }

                if (!(i < vals.length)) {
                    break;
                }
                val = vals[i++];
                if (val != null) {
                    parent.right = new TreeNode(val);
                    qNodes.offer(parent.right);
                }
            }

            return root;
        }

        @Override
        List<Integer> flatten() {
            Stack<Integer> vals = new Stack<>();

            Queue<TreeNode> qNodes = new LinkedList<>();
            qNodes.offer(this);

            while (!qNodes.isEmpty()) {
                TreeNode parent = qNodes.poll();
                if (parent == null) {
                    vals.push(null);
                }
                else {
                    vals.push(parent.val);
                    qNodes.add(parent.left);
                    qNodes.add(parent.right);
                }
            }

            while (vals.peek() == null) {
                vals.pop();
            }

            return vals;
        }

        public int val;
        public TreeNode left;
        public TreeNode right;
    }

    public static class ListNode extends Node<Integer> {
        public ListNode(int val) {
            this.val = val;
        }

        static ListNode fromIterable(Integer[] vals) {
            if (vals == null || vals.length == 0) {
                return null;
            }

            ListNode root = new ListNode(vals[0]);

            ListNode node = root;
            for (int i = 1; i < vals.length; i++) {
                node = node.next = new ListNode(vals[i]);
            }

            return root;
        }

        @Override
        List<Integer> flatten() {
            List<Integer> vals = new ArrayList<>();
            for (ListNode node = this; node != null; node = node.next) {
                vals.add(node.val);
            }
            return vals;
        }

        public int val;
        public ListNode next;
    }
}
