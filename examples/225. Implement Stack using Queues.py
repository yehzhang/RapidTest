from __future__ import print_function

from rapidtest import Result, Test, Case
from solutions.implement_stack_using_queues import Stack

with Test(Stack, operation=True) as test:
    Case('empty', Result(True),
         'push', [1],
         'empty', Result(False),
         'top', Result(1),
         'empty', Result(False),
         'pop', Result(1),
         'empty', Result(True),
         'push', [2],
         'push', [3],
         'push', [4],
         'push', [5],
         'empty', Result(False),
         'top', Result(5),
         'pop', Result(5),
         'empty', Result(False),
         'top', Result(4),
         'pop', Result(4),
         'empty', Result(False),
         'top', Result(3),
         'pop', Result(3),
         'empty', Result(False),
         'top', Result(2),
         'pop', Result(2),
         'empty', Result(True))
