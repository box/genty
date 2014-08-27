# coding: utf-8

from __future__ import unicode_literals
from unittest import TestCase

from genty import genty_dataset, genty, genty_args


@genty
class GentyArgsTest(TestCase):
    """Tests for :mod:`box.test.genty.genty_args`."""

    @genty_dataset(
        (4, 3, 2),
        ('a', 'b', 'c'),
    )
    def test_genty_args_saves_args(self, *args):
        gargs = genty_args(*args)
        self.assertItemsEqual(gargs.args, args)

    @genty_dataset(
        {
            'orange': 'orange',
            'banana': 'yellow'
        },
        {},
    )
    def test_genty_args_saves_kwargs(self, kwargs_dict):
        gargs = genty_args(**kwargs_dict)
        self.assertItemsEqual(gargs.kwargs, kwargs_dict)

    @genty_dataset(
        ((4, 3, 2), {'orange': 'orange', 'banana': 'yellow'}),
        (('a', 'b', 'c'), {}),
    )
    def test_genty_args_saves_args_and_kwargs(self, args_tuple, kwargs_dict):
        gargs = genty_args(*args_tuple, **kwargs_dict)
        self.assertItemsEqual(gargs.args, args_tuple)
        self.assertItemsEqual(gargs.kwargs, kwargs_dict)

    @genty_dataset(
        (4, 3, 2),
        ('a', 'b', 'c'),
    )
    def test_genty_args_yields_formatted_args(self, *args):
        gargs = genty_args(*args)
        self.assertItemsEqual(
            gargs,
            (repr(arg) if isinstance(arg, basestring) else unicode(arg) for arg in args),
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
        for fruit, color in kwargs_dict.iteritems():
            self.assertIn('{}={}'.format(fruit, repr(color)), gargs)

    @genty_dataset(
        ((4, 3, 2), {'orange': 'orange', 'banana': 'yellow'}),
        (('a', 'b', 'c'), {}),
    )
    def test_genty_args_yields_args_and_kwargs(self, args_tuple, kwargs_dict):
        gargs = genty_args(*args_tuple, **kwargs_dict)
        for fruit, color in kwargs_dict.iteritems():
            self.assertIn('{}={}'.format(fruit, repr(color)), gargs)
        for arg in args_tuple:
            formatted_arg = repr(arg) if isinstance(arg, basestring) else unicode(arg)
            self.assertIn(formatted_arg, gargs)
