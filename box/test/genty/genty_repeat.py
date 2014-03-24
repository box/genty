# coding: utf-8

from __future__ import unicode_literals


def genty_repeat(count):
    """
    To use in conjunction with a TestClass wrapped with @genty.

    Runs the wrapped test 'count' times:
        @genty_repeat(count)
        def test_some_function(self)
            ...

    Can also wrap a test already decorated with @genty_dataset
        @genty_repeat(3)
        @genty_dataset(True, False)
        def test_some__other_function(self, bool_value):
            ...
    This will run 6 tests in total, 3 each of the True and False cases.

    :param count:
        The number of times to run the test.
    :type count:
        `int`
    """
    if count < 0:
        raise ValueError(
            "Really? Can't have {} iterations. Please pick a value >= 0."
            .format(count)
        )

    def wrap(test_method):
        test_method.genty_repeat_count = count
        return test_method
    return wrap
