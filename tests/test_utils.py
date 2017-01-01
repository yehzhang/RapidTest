from unittest import TestCase

from rapidtest.utils import natural_format, natural_join


class TestUtils(TestCase):
    def test_natural_format(self):
        eq = self.assertEqual

        eq(natural_format('got {an}item{s}', item=[1]), 'got an item')
        eq(natural_format('got {an}item{s}', item=[1, 2]), 'got items')
        eq(natural_format('got {an}item{s}', item=[1, 2, 3]), 'got items')

        eq(natural_format('got {an}item{s}: {item}', item=[1]), 'got an item: 1')
        eq(natural_format('got {an}item{s}: {item}', item=[1, 2]), 'got items: 1 and 2')
        eq(natural_format('got {an}item{s}: {item}', item=[1, 2, 3]), 'got items: 1, 2, and 3')
        eq(natural_format('got {an}item{s}: {item}', item='123'), 'got items: 1, 2, and 3')
        eq(natural_format('got {an}item{s}: {item}', item=['123']), 'got an item: 123')

        eq(natural_format('got {a}potato{es}', item=[1]), 'got a potato')
        eq(natural_format('got {a}potato{es}', item=[1, 2]), 'got potatoes')

        with self.assertRaisesRegexp(ValueError, r'empty'):
            natural_format('got {a}item{s}', item=[])
        with self.assertRaisesRegexp(ValueError, r'empty'):
            natural_format('got {a}item{s}', item='')

        with self.assertRaises(TypeError):
            natural_format('got {a}item{s}')

    def test_natural_join(self):
        eq = self.assertEqual

        eq(natural_join('and', ''), '')
        eq(natural_join('and', '1'), '1')
        eq(natural_join('and', '12'), '1 and 2')
        eq(natural_join('and', '123'), '1, 2, and 3')
        eq(natural_join('and', []), '')

        with self.assertRaises(TypeError):
            natural_join('and', [1])
