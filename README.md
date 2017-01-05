# RapidTest

RapidTest is a Python framework for quickly creating and running test cases of your solutions to problems on certain coding practice platforms like LeetCode. One of the most powerful features of RapidTest is generating test cases in Python while testing solutions in some other languages.

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
```
```Python
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

And that's it. No more object creation or function calls. The example means that for each `Case` created, its positional arguments are passed to `Solution`'s only public method, `findMedianSortedArrays` in this case, and then the value returned is compared with `result`.


### Random testing

Generating random inputs is a painless way to come up with numerous test cases that cover corners of a solution. RapidTest supports this technique through the `test` decorator that takes a user-defined, case-generating function. Let us test the previous solution by generating random cases:

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
Running <random_numbers>: ....................................................................................................
Passed all 100 test cases
```


### Testing other languages

It is easy to test solutions in languages other than Python: just replace `Solution` class with path to the solution file. Currently supported languages: Python and Java.

```Python
# content of do_test.py
from rapidtest import Test, Case

with Test('./Solution.java'):
    Case([1, 3], [2], result=2.0)
    Case([1, 2], [3, 4], result=2.5)

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
```Java
public class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        // code here
    }
}
```

Then run it:

```
$ python do_test.py
..
Running <random_numbers>: ....x
output differs:
    findMedianSortedArrays([54, 186, 329, 339], [126, 277, 295, 398]) -> 303.0 != 286.0
```

Oops. Time to debug!


### Advanced features

- Use [operations](./advanced_features.md#using-operations) when there are multiple methods to call.


### Other features

- In addition to the `randints` function mentioned before, there are some other functions that may help generate random inputs:
    ```Python
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
- You can use `ListNode` and `TreeNode` directly in your `solution.py` like you did in the LeetCode editor without first importing them.
- Sometimes the order of returned elements in a list does not matter. You may specify this situation like:
    ```Python
    from rapidtest import Test, unordered
    from solution import Solution

    with Test(Solution, post_proc=unordered):
        pass
    ```
- Also, `post_proc` can be a post-processing function or a list of functions such that they are applied to each returned value before it is compared.
- In case a problem requires modifying arguments in place, you can specify this situation like `with Test(in_place=True)` so that all returned values are replaced by their corresponding arguments. When not all arguments are needed, you may pass `in_place` with an integer or a list of integers, each of which represents the index of an argument to replace.
- The `test` decorator can be used like `@test(200)` to specify the number of times to call the decorated function.


## Installation
Download the package and run `python setup.py install`.

This is a lightweight project that depends on the standard library only. Actually it uses Gson when testing Java solutions, but it is already included in the project, and requires neither installation nor configuration.


## Python versions
RapidTest supports Python 2.7 and 3.4+.
