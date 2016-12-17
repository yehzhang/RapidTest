from random import sample, randint, shuffle

from Solution import Solution
from rapidtest import Test, Case

with Test(Solution) as test:
    Case([""], result="")
    Case(["a"], result="a")
    Case(["aa", "a"], result="a")
    Case(["a", "b"], result="")
    Case(["ab", "bb"], result="")
    Case(["ba", "bb"], result="b")

    alphabet = "qwertyuiopasdfghjklzxcvbnm"
    alphabet = set(alphabet + alphabet.upper())

    @test
    def r(i):
        prefix_chrs = sample(alphabet, randint(0, len(alphabet)))
        shuffle(prefix_chrs)
        prefix = ''.join(prefix_chrs)

        suffix_chrs = list(alphabet - set(prefix_chrs))
        if suffix_chrs:
            strs = [prefix + suffix_chrs[i] + ''.join(sample(suffix_chrs, randint(0, len(suffix_chrs)))) for i in range(randint(1, len(suffix_chrs)))]
        else:
            strs = [prefix]
        return Case(strs, result=prefix if len(strs) > 1 else strs[0])
