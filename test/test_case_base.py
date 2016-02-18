# coding: utf-8

from __future__ import unicode_literals

from unittest import TestCase as _TestCase

import six

if not hasattr(_TestCase, 'assertItemsEqual') and not hasattr(_TestCase, 'assertCountEqual'):
    # Python 2.6 support
    # pylint:disable=import-error
    from unittest2 import TestCase as _TestCase
    # pylint:enable=import-error


class TestCase(_TestCase):
    if six.PY3:
        # pylint:disable=no-member,maybe-no-member
        assertItemsEqual = _TestCase.assertCountEqual
