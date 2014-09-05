# coding: utf-8

from __future__ import unicode_literals
import six


def format_kwarg(key, value):
    """
    Return a string of form:  "key=<value>"

    If 'value' is a string, we want it quoted. The goal is to make
    the string a named parameter in a method call.
    """
    translator = repr if isinstance(value, six.string_types) else six.text_type
    arg_value = translator(value)

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
    translator = repr if isinstance(value, six.string_types) else six.text_type
    return translator(value)


def encode_non_ascii_string(string):
    """
    :param string:
        The string to be encoded
    :type string:
        unicode or str
    :return:
        The encoded string
    :rtype:
        str
    """
    encoded_string = string.encode('utf-8', 'replace')
    if six.PY3:
        encoded_string = encoded_string.decode()

    return encoded_string
