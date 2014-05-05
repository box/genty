# coding: utf-8

from __future__ import unicode_literals

# This is an end-to-end example of the genty package in action. Consider it
# a live tutorial, showing the various features in action.

from itertools import product
from unittest import TestCase
from genty import genty, genty_repeat, genty_dataset, genty_args


@genty
class ExampleTests(TestCase):
    @genty_repeat(10)
    def test_example_of_repeat(self):
        """This test will be run 10 times"""
        pass

    @genty_dataset('red', 'orange', 'blue')
    def test_example_of_single_parameter_datasets(self, _color):
        """This test will be called 3 times, each time with a different color"""
        pass

    @genty_dataset(*product([True, False], [True, False]))
    def test_example_of_multiple_parameter_datasets(self, _first_bool, _second_bool):
        """This test is called 4 times"""
        pass

    @genty_dataset(
        some_test_case=(10, 'happy', unicode),
        another_test_case=(7, 'sleepy', float),
    )
    def test_example_of_named_datasets(self, value, message, kind):
        """This test is called for each of the 2 named datasets"""
        pass

    @genty_dataset(
        ('first', 'second', 'third'),
        genty_args('first', 'second', 'third'),
        genty_args('first', third_value='third', second_value='second')
    )
    def test_example_of_datasets_with_kwargs(self, first_value, second_value=None, third_value=None):
        """This test is called twice, with the arguments ('first', 'second', 'third').
        Note that it is not called three times, because the first and second datasets are identical."""
        pass

    @genty_repeat(4)
    @genty_dataset('first', 'second', 'third')
    def test_example_of_repeat_and_datasets(self, parameter_value):
        """This test will be called 4 times for each of the 3 possible parameter_values"""
        pass
