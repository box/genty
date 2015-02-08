# coding: utf-8

from __future__ import unicode_literals
from unittest import TestCase

from genty import genty_dataset


class GentyDatasetTest(TestCase):
    """Tests for :mod:`box.test.genty.genty_dataset`."""

    def test_empty_dataset_is_no_op(self):
        @genty_dataset()
        def some_func():
            pass

        self.assertEqual({}, some_func.genty_datasets)

    def test_single_dataset(self):
        @genty_dataset(
            ('a', 'b'),
        )
        def some_func():
            pass

        # Assert that the expected 'name' with expected value is created.
        self.assertEqual(
            {"{0}, {1}".format(repr('a'), repr('b')): ('a', 'b')},
            some_func.genty_datasets,
        )

    def test_multiple_arg_datasets(self):
        @genty_dataset(
            ('a', 'b'),
            (100, 200, '300'),
        )
        def some_func():
            pass

        # Assert that the expected 'names' with expected values are created.
        self.assertEqual(
            {"{0}, {1}".format(repr('a'), repr('b')): ('a', 'b'), "100, 200, {0}".format(repr('300')): (100, 200, '300')},
            some_func.genty_datasets,
        )

    def test_multiple_non_tuple_datasets(self):
        @genty_dataset(True, False)
        def some_func():
            pass

        # Assert that the expected 'names' with expected values are created.
        self.assertEqual(
            {'True': (True,), 'False': (False,)},
            some_func.genty_datasets,
        )

    def test_multiple_kwargs_datasets(self):
        @genty_dataset(
            some_test_case=('a', 53),
            another_case=('p', 54, 100),
            a_third_case=('x',),
        )
        def some_func():
            pass

        # Assert that the expected 'name' with expected value is created.
        self.assertEqual(
            {
                'some_test_case': ('a', 53),
                'another_case': ('p', 54, 100),
                'a_third_case': ('x',),
            },
            some_func.genty_datasets,
        )

    def test_arg_and_kwarg_datasets(self):
        @genty_dataset(
            ('a', 53),
            ('p', 54, 100),
            a_third_case=('y',),
        )
        def some_func():
            pass

        # Assert that the expected 'name' with expected value is created.
        self.assertEqual(
            {
                "{0}, 53".format(repr('a')): ('a', 53),
                "{0}, 54, 100".format(repr('p')): ('p', 54, 100),
                "a_third_case": ('y',),
            },
            some_func.genty_datasets,
        )

    def test_datasets_can_be_chained(self):
        @genty_dataset(100)
        @genty_dataset(named_set=(99,))
        @genty_dataset((1, 2))
        def some_func():
            pass

        # Assert that the expected data sets are created.
        self.assertEqual(
            {
                "100": (100,),
                "named_set": (99,),
                "1, 2": (1, 2),
            },
            some_func.genty_datasets,
        )

    def test_unicode_name_is_safely_converted(self):
        @genty_dataset(
            ('ĥȅľľő', 'ġőőďƄŷȅ'),
        )
        def some_func():
            pass

        # Assert that the expected 'names' with expected values are created.
        self.assertEqual(
            {"{0}, {1}".format(repr('ĥȅľľő'), repr('ġőőďƄŷȅ')): ('ĥȅľľő', 'ġőőďƄŷȅ')},
            some_func.genty_datasets,
        )

    def test_string_representation_is_used_to_name_dataset(self):
        class SomeClass(object):
            def __str__(self):
                return 'some-class string'

        instance = SomeClass()

        @genty_dataset(
            (instance, ),
        )
        def some_func():
            pass

        # Assert that the expected 'names' with expected values are created.
        self.assertEqual(
            {'some-class string': (instance,)},
            some_func.genty_datasets,
        )
