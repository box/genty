# coding: utf-8

from __future__ import unicode_literals
import six
from unittest import TestCase
if not hasattr(TestCase, 'assertItemsEqual') and not hasattr(TestCase, 'assertCountEqual'):
    # Python 2.6 support
    # pylint:disable=import-error
    from unittest2 import TestCase
    # pylint:enable=import-error

from box.test.genty import genty_dataset, genty
from box.test.genty.genty_args import genty_args
from box.test.genty.private import format_arg


@genty
class GentyArgsTest(TestCase):
    """Tests for :mod:`box.test.genty.genty_args`."""

    def _assert_items_equal(self, first, second, msg=None):
        if hasattr(self, 'assertItemsEqual'):
            return self.assertItemsEqual(first, second, msg)
        else:
            # Python 3.3+ support
            # pylint:disable=all
            return self.assertCountEqual(first, second, msg)
            # pylint:enable=all

    @genty_dataset(
        (4, 3, 2),
        ('a', 'b', 'c'),
    )
    def test_genty_args_saves_args(self, *args):
        gargs = genty_args(*args)
        self._assert_items_equal(gargs.args, args)

    @genty_dataset(
        {
            'orange': 'orange',
            'banana': 'yellow'
        },
        {},
    )
    def test_genty_args_saves_kwargs(self, kwargs_dict):
        gargs = genty_args(**kwargs_dict)
        self._assert_items_equal(gargs.kwargs, kwargs_dict)

    @genty_dataset(
        ((4, 3, 2), {'orange': 'orange', 'banana': 'yellow'}),
        (('a', 'b', 'c'), {}),
    )
    def test_genty_args_saves_args_and_kwargs(self, args_tuple, kwargs_dict):
        gargs = genty_args(*args_tuple, **kwargs_dict)
        self._assert_items_equal(gargs.args, args_tuple)
        self._assert_items_equal(gargs.kwargs, kwargs_dict)

    @genty_dataset(
        (4, 3, 2),
        ('a', 'b', 'c'),
    )
    def test_genty_args_yields_formatted_args(self, *args):
        gargs = genty_args(*args)
        self._assert_items_equal(
            gargs,
            (format_arg(arg) for arg in args),
        )

    @genty_dataset(
        {
            'orange': 'orange',
            'banana': 'yellow'
        },
        {},
    )
    def test_genty_args_yields_kwargs(self, kwargs_dict):
        gargs = genty_args(**kwargs_dict)
        for fruit, color in six.iteritems(kwargs_dict):
            self.assertIn('{0}={1}'.format(fruit, repr(color)), gargs)

    @genty_dataset(
        ((4, 3, 2), {'orange': 'orange', 'banana': 'yellow'}),
        (('a', 'b', 'c'), {}),
    )
    def test_genty_args_yields_args_and_kwargs(self, args_tuple, kwargs_dict):
        gargs = genty_args(*args_tuple, **kwargs_dict)
        for fruit, color in six.iteritems(kwargs_dict):
            self.assertIn('{0}={1}'.format(fruit, repr(color)), gargs)
        for arg in args_tuple:
            formatted_arg = format_arg(arg)
            self.assertIn(formatted_arg, gargs)
