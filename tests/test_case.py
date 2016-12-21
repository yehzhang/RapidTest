from unittest import TestCase

from rapidtest import Case, Result
from rapidtest.executors import OperationStub
from rapidtest.utils import nop


class TestCase_(TestCase):
    def test_process_args(self):
        c = Case()

        res = c.process_args([1, 2, 3], False)
        self.assertEqual(res, ((), [OperationStub(None, [1, 2, 3], True)], []))

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
        self.assertEqual(res, (('a', 2, 'c'), [
            OperationStub('push', [1, 2, 3], False),
            OperationStub('pop', collect=True),
            OperationStub('count'),
            OperationStub('count'),
            OperationStub('pop', collect=True),
            OperationStub('push', [[4, 5]], True),
            OperationStub('len'),
        ], [Result(1), Result('d'), Result([0])]))

        STRS = [
            ([], r'No operation is specified'),
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

    def test__initialize(self):
        with self.assertRaisesRegexp(RuntimeError, r'Target.*not specified'):
            Case('a', Result(1), operation=True)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'Both'):
            Case('a', Result(1), result=1, target=nop)._initialize()
        with self.assertRaisesRegexp(RuntimeError, r'Both'):
            Case('a', Result(2), operation=True, result=None, target=nop)._initialize()

        Case('a', result=1, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'object.*not specified'):
            Case('a', operation=True, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'keyword.*not specified'):
            Case('a', target=nop)._initialize()

        Case('a', Result(2), operation=True, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'keyword.*target.*operation is True'):
            Case('a', operation=True, result=None, target=nop)._initialize()
        Case('a', operation=True, result=list, target=nop)._initialize()

        with self.assertRaisesRegexp(RuntimeError, r'object.*not accepted'):
            Case('a', Result(2), target=nop)._initialize()
