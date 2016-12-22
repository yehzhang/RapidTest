from __future__ import print_function

from Solution import LRUCache
from rapidtest import Result, Test, Case

with Test(LRUCache, operation=True) as test:
    Case([4],
         'get', [1], Result(-1),
         'set', [1, 1],
         'set', [2, 2],
         'set', [3, 3],
         'set', [4, 4],
         'get', [1], Result(1),
         'get', [2], Result(2),
         'get', [3], Result(3),
         'get', [4], Result(4),
         'get', [5], Result(-1),
         'get', [1], Result(1),
         'set', [5, 5],
         'get', [2], Result(-1),
         'get', [1], Result(1),
         'set', [6, 6],
         'get', [1], Result(1),
         'get', [3], Result(-1))

    Case([3],
         'set', [1, 1],
         'set', [2, 2],
         'set', [3, 3],
         'set', [4, 4],
         'get', [4], Result(4),
         'get', [3], Result(3),
         'get', [2], Result(2),
         'get', [1], Result(-1),
         'set', [5, 5],
         'get', [1], Result(-1),
         'get', [2], Result(2),
         'get', [3], Result(3),
         'get', [4], Result(-1),
         'get', [5], Result(5))

    Case([2],
         'set', [2, 1],
         'set', [2, 2],
         'get', [2], Result(2),
         'set', [1, 1],
         'set', [4, 1],
         'get', [2], Result(-1))
