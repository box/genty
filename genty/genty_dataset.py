# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict
from .genty_args import GentyArgs
from .private import format_arg


def genty_dataset(*args, **kwargs):
    """Decorator defining data sets to provide to a test.

    Inspired by http://sebastian-bergmann.de/archives/
    702-Data-Providers-in-PHPUnit-3.2.html

    The canonical way to call @genty_dataset, with each argument each
    representing a data set to be injected in the test method call:
        @genty_dataset(
            ('a1', 'b1'),
            ('a2', 'b2'),
        )
        def test_some_function(a, b)
            ...

    If the test function takes only one parameter, you can replace the tuples
    by a single value. So instead of the more verbose:
        @genty_dataset(
            ('c1',),
            ('c2',),
        )
        def test_some_other_function(c)
            ...

    One can write:
        @genty_dataset('c1', 'c2')
        def test_some_other_function(c)
            ...

    For each set of arguments, a suffix identifying that argument set is
    built by concatenating the string representation of the arguments
    together. You can control the test names for each data set by passing
    the data sets as keyword args, where the keyword is the desired suffix.
    For example:
        @genty_dataset(
            ('a1', 'b1),
        )
        def test_function(a, b)
            ...
    produces a test named 'test_function_for_a1_and_b1', while
        @genty_dataset(
            happy_path=('a1', 'b1'),
        )
        def test_function(a, b)
            ...
    produces a test named test_function_for_happy_path. These are just
    parameters to a method call, so one can have unnamed args first
    followed by keyword args
        @genty_dataset(
            ('x', 'y'),
            ('p', 'q'),
            Monday=('a1', 'b1'),
            Tuesday=('t1', 't2'),
        )
        def test_function(a, b)
            ...

    :param args:
        Tuple of unnamed data sets.
    :type args:
        `tuple` of varies
    :param kwargs:
        Dict of pre-named data sets.
    :type kwargs:
        `dict` of `unicode` to varies
    """
    datasets = _build_datasets(*args, **kwargs)

    def wrap(test_method):
        # Save the datasets in the test method. This data will be consumed
        # by the @genty decorator.
        test_method.genty_datasets = datasets
        return test_method
    return wrap


def _build_datasets(*args, **kwargs):
    """Build the datasets into a dict, where the keys are the name of the
    data set and the values are the data sets themselves.

    :param args:
        Tuple of unnamed data sets.
    :type args:
        `tuple` of varies
    :param kwargs:
        Dict of pre-named data sets.
    :type kwargs:
        `dict` of `unicode` to varies
    :return:
        The dataset dict.
    :rtype:
        `dict`
    """
    datasets = OrderedDict()
    _add_arg_datasets(datasets, args)
    _add_kwarg_datasets(datasets, kwargs)
    return datasets


def _add_arg_datasets(datasets, args):
    """Add data sets of the given args.

    :param datasets:
        The dict where to accumulate data sets.
    :type datasets:
        `dict`
    :param args:
        Tuple of unnamed data sets.
    :type args:
        `tuple` of varies
    """
    for dataset in args:
        # turn a value into a 1-tuple.
        if not isinstance(dataset, (tuple, GentyArgs)):
            dataset = (dataset,)

        # Create a test_name_suffix - basically the parameter list
        if isinstance(dataset, GentyArgs):
            dataset_strings = dataset     # GentyArgs supports iteration
        else:
            dataset_strings = [format_arg(data) for data in dataset]
        test_method_suffix = ", ".join(dataset_strings)

        datasets[test_method_suffix] = dataset


def _add_kwarg_datasets(datasets, kwargs):
    """Add data sets of the given kwargs.

    :param datasets:
        The dict where to accumulate data sets.
    :type datasets:
        `dict`
    :param kwargs:
        Dict of pre-named data sets.
    :type kwargs:
        `dict` of `unicode` to varies
    """
    for test_method_suffix, dataset in kwargs.iteritems():
        datasets[test_method_suffix] = dataset
