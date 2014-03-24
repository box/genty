# coding: utf-8

from __future__ import unicode_literals


def format_kwarg(key, value):
    """
    Return a string of form:  "key=<value>"

    If 'value' is a string, we want it quoted. The goal is to make
    the string a named parameter in a method call.
    """
    translator = repr if isinstance(value, basestring) else unicode
    arg_value = translator(value)

    return '{}={}'.format(key, arg_value)


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
    return repr(value) if isinstance(value, basestring) else unicode(value)
