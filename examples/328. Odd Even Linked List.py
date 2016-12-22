from __future__ import print_function

from random import randint

from Solution import Solution
from rapidtest import Test, Case, randints, ListNode, randbool

with Test(Solution) as test:
    Case(ListNode.from_iterable([1, 2, 3, 4, 5, 6, 7, 8]),
         result=ListNode.from_iterable([1, 3, 5, 7, 2, 4, 6, 8]))
    Case(ListNode.from_iterable([]), result=ListNode.from_iterable([]))
    Case(ListNode.from_iterable([1]), result=ListNode.from_iterable([1]))
    Case(ListNode.from_iterable([1, 2]), result=ListNode.from_iterable([1, 2]))


    @test
    def r(i):
        cnt_vals = randint(0, i)
        odd_vals = randints(cnt_vals)
        even_vals = randints(cnt_vals)

        vals = [val for pair in zip(odd_vals, even_vals) for val in pair]
        if even_vals and randbool():
            even_vals.pop()
            vals.pop()
        root = ListNode.from_iterable(vals)

        odd_root = ListNode.from_iterable(odd_vals)
        if odd_root:
            even_root = ListNode.from_iterable(even_vals)
            odd_root.end().next = even_root

        return Case(root, result=odd_root)
