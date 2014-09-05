# coding: utf-8

from __future__ import unicode_literals
from itertools import chain
import six
from .private import format_arg, format_kwarg


class GentyArgs(object):
    """
    Store args and kwargs for use in a genty-generated test.
    """
    def __init__(self, *args, **kwargs):
        super(GentyArgs, self).__init__()
        self._args = args
        self._kwargs = kwargs

    @property
    def args(self):
        """Return tuple of positional arguments to be passed to the test."""
        return self._args

    @property
    def kwargs(self):
        """Return dictionary of keyword arguments to be passed to the test."""
        return self._kwargs

    def __iter__(self):
        """Allow iterating over the argument list.
        First, yield value of args in given order.
        Then yield kwargs in sorted order, formatted as key_equals_value.
        """
        sorted_kwargs = sorted(six.iteritems(self._kwargs))
        return chain(
            (format_arg(arg) for arg in self._args),
            (format_kwarg(k, v) for k, v in sorted_kwargs),
        )


def genty_args(*args, **kwargs):
    """
    Used to pass args and kwargs to a test wrapped with @genty_dataset.

    Runs the test with the same arguments and keyword arguments passed
    to genty_args. genty_args is usefule for tests with a large number of
    arguments or optional arguments.

    To use, simply pass your arguments and keyword arguments to genty_args
    in the same way you'd like them to be passed to your test:
        @genty_dataset(
            genty_args('a1', 'b1', 1, 'd1'),
            genty_args('a2', 'b2', d='d2')
        )
        def test_function(a, b, c=0, d=None)
            ...

    For each genty_args call, a suffix identifying the arguments will be built
    by concatenating the positional argument values, and then concatenating the
    keyword argument names and values (formatted like parameter_equals_value).
    For example:

        @genty_dataset(
            genty_args('a1', 'b1', 1, 'd1'),
            genty_args('a2', 'b2', d='d2')
        )
        def test_function(a, b, c=0, d=None)
            ...
    produces tests named
        test_function('a1', 'b1', 1, 'd1') and
        test_function('a2', 'b2', d='d2')

    :param args:
        Ordered arguments that should be sent to the test.
    :type args:
        `tuple` of varies
    :param kwargs:
        Keyword arguments that should be sent to the test.
    :type kwargs:
        `dict` of `unicode` to varies
    """
    return GentyArgs(*args, **kwargs)
