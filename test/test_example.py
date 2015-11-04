# coding: utf-8

from __future__ import unicode_literals

# This is an end-to-end example of the genty package in action. Consider it
# a live tutorial, showing the various features in action.

from itertools import product
from unittest import TestCase
from genty import genty, genty_repeat, genty_dataset, genty_args, genty_dataprovider


@genty
class ExampleTests(TestCase):

    # This is set so that if nosetest's multi-processing capability is being used, the
    # tests in this class can be split across processes.
    _multiprocess_can_split_ = True

    def setUp(self):
        super(ExampleTests, self).setUp()

        # Imagine that _some_function is actually some http request that can
        # only be called *after* authentication happens in this setUp method
        self._some_function = lambda x, y: ((x + y), (x - y), x * y)

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
        some_test_case=(10, 'happy', str),
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

    @genty_dataset(10, 100)
    @genty_dataset('first', 'second', 'third')
    def test_example_of_composing_datasets(self, parameter_value):
        """This test will be called 5 times for each of the values in the 2 datasets above"""
        pass

    @genty_dataset((1000, 100), (100, 1))
    def calculate(self, x_val, y_val):
        return self._some_function(x_val, y_val)

    @genty_dataprovider(calculate)
    def test_heavy(self, data1, data2, data3):
        """
        This test will be called 2 times because the data_provider - the
        calculate helper - has 2 datasets
        """

    def no_dataset(self):
        return self._some_function(100, 200)

    @genty_dataprovider(no_dataset)
    def test_dataprovider_with_no_dataset(self, data1, data2, data3):
        """
        Uses a dataprovider that has no datasets.
        """

    @genty_dataset('127.0.0.1')
    def test_with_period_char_in_dataset(self, arg):
        """
        A dataset with a '.' doesn't screw up nosetests --processes=4
        """
