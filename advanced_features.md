### Using operations

For example, let us implement queue using stacks.

```Python
# content of solution.py
class Queue(object):
    def __init__(self):
        # code here

    def push(self, x):
        # code here

    def pop(self):
        # code here

    def empty(self):
        # code here
```

When multiple methods in a solution class are to be called, operations come in handy. Operations are a sequence of method names, each of which is optionally followed by arguments and asserted result, where method name represents its corresponding method to be called, and asserted result is a `Result` object containing the value returned by calling the method with arguments.

```Python
# content of do_test.py
from rapidtest import Test, Case, Result
from solution import Queue

with Test(Queue, operation=True):
    Case('empty', Result(True),
         'push',  [1],
         'empty', Result(False),
         'push',  [2],
         'pop',   Result(2),
         'pop',   Result(1),
         'empty', Result(True))
```

What's more, the first argument of `Case` can be a list of arguments to be passed to the constructor of a solution class:

```Python
# content of solution.py
# Implement an iterator over a binary search tree (BST).
class BSTIterator(object):
    def __init__(self, root):
        """
        :type root: TreeNode
        """
        # code here

    def hasNext(self):
        # code here

    def next(self):
        # code here

# Your BSTIterator will be called like this:
# i, v = BSTIterator(root), []
# while i.hasNext(): v.append(i.next())


# content of do_test.py
from rapidtest import Test, Case, Result, TreeNode
from solution import BSTIterator

with Test(BSTIterator, operation=True):
    root = TreeNode.from_iterable([1, 2, 3])
    Case([root],
         'hasNext', Result(True),
         'next',    Result(2),
         'hasNext', Result(True),
         'next',    Result(1),
         'hasNext', Result(True),
         'next',    Result(3),
         'hasNext', Result(False))
```
