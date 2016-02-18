# coding: utf-8

from __future__ import unicode_literals
from genty import genty_repeat
from test.test_case_base import TestCase


class GentyRepeatTest(TestCase):
    """Tests for :mod:`box.test.genty.genty_repeat`."""

    def test_repeat_decorator_decorates_function_with_appropriate_repeat_count(self):
        @genty_repeat(15)
        def some_func():
            pass

        self.assertEqual(15, some_func.genty_repeat_count)  # pylint:disable=no-member

    def test_repeat_decorator_decorates_method_with_appropriate_repeat_count(self):
        class SomeClass(object):
            @genty_repeat(13)
            def some_func(self):
                pass

        some_instance = SomeClass()

        self.assertEqual(13, some_instance.some_func.genty_repeat_count)  # pylint:disable=no-member

    def test_repeat_rejects_negative_counts(self):
        with self.assertRaises(ValueError) as context:
            @genty_repeat(-1)
            def _():
                pass

        self.assertIn('Please pick a value >= 0', str(context.exception))

    def test_repeat_allows_zero_iterations(self):
        @genty_repeat(0)
        def some_func():
            pass

        self.assertEqual(0, some_func.genty_repeat_count)   # pylint:disable=no-member
