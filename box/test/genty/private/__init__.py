# coding: utf-8

from __future__ import unicode_literals


try:
    isinstance('', basestring)
    isinstance('', unicode)

    def _isstr(value):
        return isinstance(value, basestring)

    def _tostr(value):
        return unicode(value)
except NameError:
    def _isstr(value):
        return isinstance(value, str)

    def _tostr(value):
        return str(value)


def format_kwarg(key, value):
    """
    Return a string of form:  "key=<value>"

    If 'value' is a string, we want it quoted. The goal is to make
    the string a named parameter in a method call.
    """
    arg_value = repr(value) if _isstr(value) else _tostr(value)

    return '{0}={1}'.format(key, arg_value)


def format_arg(value):
    """
    :param value:
        Some value in a dataset.
    :type value:
        varies
    :return:
        unicode representation of that value
    :rtype:
        `unicode`
    """
    return repr(value) if _isstr(value) else _tostr(value)
