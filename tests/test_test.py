from unittest import TestCase

from rapidtest import Result, Test, Case


class TestTest(TestCase):
    def test_check_result(self):
        t = Test(list, operation=True)

        t.add_case(Case('append', [1],
                        'pop', Result(1),
                        'append', [2],
                        'append', [3],
                        'pop',
                        'pop', Result(2)))
        t.add_case(Case('append', [1],
                        'pop',
                        'append', [2],
                        'append', [3],
                        'pop',
                        'pop', result=list))
        t.run()

        t.add_case(Case('append', [1],
                        'pop', Result(2)))
        t.add_case(Case('append', [1],
                        'pop', Result(1)))
        with self.assertRaisesRegexp(ValueError, r'differ'):
            t.run()
        t.run()


    def test_summary(self):
        def assert_sum_code(c):
            code, _ = t.summary()
            self.assertEqual(code, c)

        t = Test(list, operation=True)
        assert_sum_code(t.EXIT_EMPTY)

        t.add_case(Case('append', [1], 'pop', Result(1)))
        t.run()
        assert_sum_code(t.EXIT_PASS)

        t.add_case(Case('pop', Result(None)))
        assert_sum_code(t.EXIT_PENDING)
        with self.assertRaises(IndexError):
            t.run()
        assert_sum_code(t.EXIT_FAIL)
        t.add_case(Case('append', [1], Result(None)))
        assert_sum_code(t.EXIT_PENDING)
        t.run()
        assert_sum_code(t.EXIT_FAIL)

        def f(i):
            if i == 0:
                return Case('append', [1], Result(None))
            raise ValueError
        t.add_func(f)
        with self.assertRaises(ValueError):
            t.run()
        assert_sum_code(t.EXIT_GEN_ERR)
