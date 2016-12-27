# RapidTest

RapidTest is a Python framework for quickly creating and running test cases of your solutions to problems on coding practice platforms like LeetCode.

RapidTest aims to increase acceptance of your solutions by facilitating creating test cases. The more comprehensive the test is, the less likely the solution is to fail. And this is not the only benefit of testing your solutions. Receiving feedback from a judge right after finishing a solution helps, but why not first exploit the problem from the perspective of its inputs? In some cases, RapidTest identifies inputs that fail your solution before submission, thus saving your time waiting for judging, and, if you are participating in an online contest, avoiding penalties.


## Introduction

To get started, let us write test cases of a solution that finds the median of numbers from two sorted arrays:

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

Then run it:

```
$ python do_tests.py
..
Passed all 2 test cases
```

And that's it. No more object creation or function calls. What the example does is simple: for each `Case` created, its positional arguments are passed to `Solution`'s only public method, `findMedianSortedArrays` in this case, and then the value returned is compared with `result`.


### Random testing

Generating random inputs is a painless way to come up with numerous test cases that cover corners of a solution. RapidTest supports this technique through the _`test` decorator_ that takes a user-defined, case-generating function. Let us test the previous solution by generating random cases:

```Python
# content of do_test.py
from rapidtest import Test, Case, randints
from statistics import median
from solution import Solution

with Test(Solution) as test:
    @test
    def random_numbers(i):
        """
        :param int i: number of times this function is called starting from 0
        :return Case:
        """
        nums1 = sorted(randints(count=i, max_num=i * 100))
        nums2 = sorted(randints(count=max(i, 1), max_num=i * 100))
        result = float(median(nums1 + nums2))
        return Case(nums1, nums2, result=result)
```

Then run it:

```
$ python do_test.py
....................................................................................................
Passed all 100 test cases
```

What's more, there are some other functions that may help generate random inputs:

```
>>> from RapidTest import TreeNode, randints, randstr

>>> TreeNode.make_random(10, duplicate=False)
TreeNode(5, (0, #, (9, #, (3, 1, 8))), (7, (4, 6, 2), #))

>>> TreeNode.make_random(10, binary_search=True)
TreeNode(6, (3, (1, 0, 2), (5, 4, #)), (8, 7, 9))

>>> randints(7, unique=True, min_num=10, max_num=20)
[11, 20, 14, 10, 15, 17, 19]

>>> from string import ascii_lowercase
>>> randstr(length=10, unique=True, alphabet=ascii_lowercase)
'lpmtyfxusv'
```


### Advanced features

- (Using operations)[./advanced_features.md#using-operations] when there are multiple methods to be called.


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
- The `test` decorator can be used like `@test(200)` to specify the number of times to call the decorated function.


## Installation
```
$ python setup.py install
```

## Python versions
RapidTest supports Python 2.7 and 3.4+.
