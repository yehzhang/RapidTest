# RapidTest

RapidTest is a Python framework for quickly testing solutions on coding practice platforms like LeetCode.

RapidTest aims to increase acceptance of your solutions by facilitating writing test cases. Receiving feedback from a judge right after finishing a solution helps, but why not first exploit the problem from the perspective of its inputs? In some cases, RapidTest identifies inputs that fail your solution before submission, thus saving your time waiting for judging, and, if you are participating in an online contest, avoiding penalties.


## Introduction

To get started, let us test a solution that finds the median of numbers from two sorted arrays.

```Python
# content of do_test.py
from rapidtest import Test, Case
from solution import Solution

with Test(Solution):
    Case([1, 3], [2], result=2.0)
    Case([1, 2], [3, 4], result=2.5)


# content of solution.py
class Solution(object):
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        # code here
```

```
$ python do_tests.py
..
Passed all 2 test cases
```

And that's it. No more object creation or function calls. What the example does is simple: for each `Case` created, its positional arguments are passed to `Solution`'s only public method `findMedianSortedArrays`, and then the value returned is compared with `result`.


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


### Random testing

Generating random inputs is a painless way to come up with numerous test cases that cover corners of a solution. RapidTest supports this technique by making `Test()` object a decorator that takes a user-defined, case-generating function. Let us still look at the `BSTIterator` solution:

```Python
from rapidtest import Test, Case, Result, TreeNode
from solution import BSTIterator

with Test(BSTIterator, operation=True) as test:
    @test
    def random_case(i):
        """
        :param int i: number of times this function is called starting from 0
        :return Case:
        """
        root = TreeNode.make_random(size=i)
        return _make_case(root)

    @test(50)
    def random_case_with_duplicate_nodes(i):
        root = TreeNode.make_random(size=i, duplicate=True)
        return _make_case(root)

    def _make_case(root):
        operations = []

        # Constructor arguments
        operations.append([root])

        # Methods names and asserted results
        if root is not None:
            for val in root.inorder():
                operations.extend(['hasNext', Result(True), 'next', Result(val)])
        operations.extend(['hasNext', Result(False)])

        return Case(*operations)
```

```
$ python do_test.py
....................................................................................................
..................................................
Passed all 150 test cases
```

What's more, there are some other functions that may help generate random inputs:

```
>>> TreeNode.make_random(10)
TreeNode(5, (0, #, (9, #, (3, 1, 8))), (7, (4, 6, 2), #))

>>> TreeNode.make_random(10, binary_search=True)
TreeNode(6, (3, (1, 0, 2), (5, 4, #)), (8, 7, 9))

>>> randints(count=7, unique=True, min_num=10, max_num=20)
[11, 20, 14, 10, 15, 17, 19]

>>> from string import ascii_lowercase
>>> randstr(length=10, unique=True, alphabet=ascii_lowercase)
'lpmtyfxusv'
```


### Other features

- You can use `ListNode` and `TreeNode` in your `solution.py` without first importing them like you did in the LeetCode editor.

- Sometimes the order of returned elements in a list does not matter. You may specify this situation like:
    ```Python
    from rapidtest import Test, unordered
    from solution import Solution

    with Test(Solution, post_proc=unordered):
        pass
    ```

- In fact, post_proc can be a post-processing function or a list of functions such that they are applied to each returned value before it is compared.


## Installation
```
$ python setup.py install
```

## Python versions
RapidTest supports Python 2.7 and 3.4+.
