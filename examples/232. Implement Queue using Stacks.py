from __future__ import print_function

from rapidtest import Result, Test, Case
from solutions.implement_queue_using_stacks import Queue

with Test(Queue, operation=True) as test:
    Case('empty', Result(True),
         'push', [1],
         'empty', Result(False),
         'peek', Result(1),
         'empty', Result(False),
         'pop', Result(1),
         'empty', Result(True),
         'push', [2],
         'push', [3],
         'push', [4],
         'push', [5],
         'empty', Result(False),
         'peek', Result(2),
         'pop', Result(2),
         'empty', Result(False),
         'peek', Result(3),
         'pop', Result(3),
         'empty', Result(False),
         'peek', Result(4),
         'pop', Result(4),
         'empty', Result(False),
         'peek', Result(5),
         'pop', Result(5),
         'empty', Result(True))
