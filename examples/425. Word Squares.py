from rapidtest import Test, Case, randints, randstr, Result, unordered
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java', post_proc=unordered) as t:
    Case(['area', 'lead', 'wall', 'lady', 'ball'], result=[
        [
            'wall',
            'area',
            'lead',
            'lady'
        ], [
            'ball',
            'area',
            'lead',
            'lady'
        ]
    ])

    Case(['abat', 'baba', 'atan', 'atal'], result=[
        [
            'baba',
            'abat',
            'baba',
            'atan'
        ], [
            'baba',
            'abat',
            'baba',
            'atal'
        ]
    ])

    Case(['a'], result=[
        [
            'a',
        ]
    ])

    Case(['ab', 'ba'], result=[
        [
            'ab',
            'ba',
        ], [
            'ba',
            'ab',
        ]
    ])

    Case(['abc', 'bca', 'cab'], result=[
        [
            'abc',
            'bca',
            'cab',
        ], [
            'bca',
            'cab',
            'abc',
        ], [
            'cab',
            'abc',
            'bca',
        ]
    ])
