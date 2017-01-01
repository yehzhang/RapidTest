from unittest import TestCase

from rapidtest.executors import ExternalExecutorFabric, Java8Executor


class TestExternalExecutorFabric(TestCase):
    def test_supported_environments(self):
        self.assertTrue(ExternalExecutorFabric.supported_environments())

    def test_guess(self):
        self.assertIs(ExternalExecutorFabric.guess('123.java'), Java8Executor)

        with self.assertRaisesRegexp(ValueError, r'environment: Java'):
            ExternalExecutorFabric.guess('1.py')
