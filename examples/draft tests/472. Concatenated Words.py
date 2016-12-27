from __future__ import print_function

from Solution import Solution
from rapidtest import Test, Case, unordered

with Test(Solution, post_proc=unordered) as test:
    Case([], result=[])
    Case(['a'], result=[])
    Case(['a', 'b'], result=[])
    Case(['a', 'b', 'ab'], result=['ab'])
    Case(['a', 'b', 'aab'], result=['aab'])
    Case(['a', 'b', 'acb'], result=[])
    Case(['a', 'ac', 'b', 'acb'], result=['acb'])
    Case([''], result=[])
    Case(['', 'a'], result=[])
    Case(['', 'a', 'ab'], result=[])
    Case(['', 'a', 'ab', 'b'], result=['ab'])
    Case(['', 'a', 'acb', 'b'], result=[])
    Case(['', 'a', 'acb', 'b', 'c'], result=['acb'])
    Case(['cat', 'cats', 'catsdogcats', 'dog', 'dogcatsdog', 'hippopotamuses', 'rat',
          'ratcatdogcat'], result=['catsdogcats', 'dogcatsdog', 'ratcatdogcat'])
