from random import randint
from unittest import TestCase

from rapidtest import Case, Result
from rapidtest.executors import Operation, Operations
from rapidtest.utils import nop, identity, randints


class TestCase_(TestCase):
    def test_process_args(self):
        c = Case()

        res = c.process_args([1, 2, 3], False)
        self.assertEqual(res, Operations((), [Operation(None, [1, 2, 3], True)]))

        res = c.process_args([
            ['a', 2, 'c'],
            'push', [1, 2, 3],
            'pop', Result(1),
            'count',
            'count',
            'pop', Result('d'),
            'push', [[4, 5]], Result([0]),
            'len'
        ], True)
        self.assertEqual(res, Operations(('a', 2, 'c'), [
            Operation('push', [1, 2, 3], False),
            Operation('pop', collect=True),
            Operation('count'),
            Operation('count'),
            Operation('pop', collect=True),
            Operation('push', [[4, 5]], True),
            Operation('len'),
        ]))

        STRS = [
            ([], r'No.*is specified'),
            ([
                 [1, 2, 3],
                 []
             ], r'expected.*, got \[\]'),
            ([
                 [1, 2, 3],
                 'a', [], [1]
             ], r'expected.*, got \[1\]'),
            ([
                 'a', Result(1), Result(2)
             ], r'expected.*, got Result\(2\)'),
            ([
                 Result(1),
             ], r'got Result\(1\)'),
            ([
                 [1, 2, 3],
                 Result(1)
             ], r'got Result\(1\)'),
            ([
                 '1', Result('b'), [1]
             ], r'got \[1\]'),
        ]

        for args, pat in STRS:
            with self.assertRaisesRegexp(ValueError, pat):
                c.process_args(args, True)

        with self.assertRaisesRegexp(ValueError, r'[nN]o args'):
            c.process_args([], True)

        with self.assertRaisesRegexp(ValueError, r'no method call'):
            c.process_args([[]], True)

    def test__initialize(self):
        with self.assertRaisesRegexp(RuntimeError, r'Target.*specified.*neither'):
            Case('append', Result(1), operation=True)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'Both'):
            Case('append', Result(1), result=1, target=nop)._initialize()
        with self.assertRaisesRegexp(RuntimeError, r'Both'):
            Case('append', Result(2), operation=True, result=None, target=nop)._initialize()

        Case('append', result=1, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'object.*not specified'):
            Case('append', operation=True, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'result.*not specified'):
            Case('append', target=nop)._initialize()

        Case('append', Result(2), operation=True, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'keyword.*target.*operation is True'):
            Case('append', operation=True, result=None, target=nop)._initialize()
        Case('append', operation=True, result=list, target=nop)._initialize()

        with self.assertRaises(AttributeError):
            Case('a', operation=True, result=list, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'object.*not accepted'):
            Case('append', Result(2), target=nop)._initialize()

    def test_preprocess_in_place(self):
        f = Case.preprocess_in_place(True)
        self.assertEqual(f, identity)

        f = Case.preprocess_in_place(False)
        self.assertIsNone(f)

        for i in range(1, 100):
            args = randints(i, max_num=i * 100)

            idx = randint(0, i - 1)
            f = Case.preprocess_in_place(idx)
            self.assertEqual(f(args), args[idx])

            indices = randints(randint(1, i), unique=True, max_num=i - 1)
            f = Case.preprocess_in_place(indices)
            self.assertEqual(f(args), [args[idx] for idx in indices])

        with self.assertRaises(TypeError):
            Case.preprocess_in_place('123')
        with self.assertRaises(TypeError):
            Case.preprocess_in_place(['123'])
        with self.assertRaises(TypeError):
            Case.preprocess_in_place('')
        with self.assertRaises(TypeError):
            Case.preprocess_in_place(1.1)
        with self.assertRaises(TypeError):
            Case.preprocess_in_place([1.1])
        with self.assertRaises(ValueError):
            Case.preprocess_in_place([])
