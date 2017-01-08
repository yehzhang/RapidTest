from unittest import TestCase

from rapidtest.executors.python.dependencies import get_dependencies


class TestExecutor(TestCase):
    def test_get_dependencies(self):
        get_dependencies()
