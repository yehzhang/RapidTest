from unittest import TestCase

from rapidtest.executors import get_dependency


class TestExecutor(TestCase):
    def test_get_dependency(self):
        get_dependency()
