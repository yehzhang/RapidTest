from unittest import TestCase

from rapidtest.executors import get_dependencies


class TestExecutor(TestCase):
    def test_get_dependencies(self):
        get_dependencies()
