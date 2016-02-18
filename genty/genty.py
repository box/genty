# coding: utf-8

from __future__ import absolute_import, unicode_literals

import functools
from itertools import chain
import math
import re
import sys
import types

import six

from .genty_args import GentyArgs
from .private import encode_non_ascii_string


REPLACE_FOR_PERIOD_CHAR = '\xb7'


def genty(target_cls):
    """
    This decorator takes the information provided by @genty_dataset,
    @genty_dataprovider, and @genty_repeat and generates the corresponding
    test methods.

    :param target_cls:
        Test class whose test methods have been decorated.
    :type target_cls:
        `class`
    """
    tests = _expand_tests(target_cls)
    tests_with_datasets = _expand_datasets(tests)
    tests_with_datasets_and_repeats = _expand_repeats(tests_with_datasets)

    _add_new_test_methods(target_cls, tests_with_datasets_and_repeats)

    return target_cls


def _expand_tests(target_cls):
    """
    Generator of all the test unbound functions in the given class.

    :param target_cls:
        Target test class.
    :type target_cls:
        `class`
    :return:
        Generator of all the test_methods in the given class yielding
        tuples of method name and unbound function.
    :rtype:
        `generator` of `tuple` of (`unicode`, `function`)
    """
    entries = dict(six.iteritems(target_cls.__dict__))
    for key, value in six.iteritems(entries):
        if key.startswith('test') and isinstance(value, types.FunctionType):
            if not hasattr(value, 'genty_generated_test'):
                yield key, value


def _expand_datasets(test_functions):
    """
    Generator producing test_methods, with an optional dataset.

    :param test_functions:
        Iterator over tuples of test name and test unbound function.
    :type test_functions:
        `iterator` of `tuple` of (`unicode`, `function`)
    :return:
        Generator yielding a tuple of
        - method_name      : Name of the test method
        - unbound function : Unbound function that will be the test method.
        - dataset name     : String representation of the given dataset
        - dataset          : Tuple representing the args for a test
        - param factory    : Function that returns params for the test method
    :rtype:
        `generator` of `tuple` of (
            `unicode`,
            `function`,
            `unicode` or None,
            `tuple` or None,
            `function` or None,
        )
    """
    for name, func in test_functions:

        dataset_tuples = chain(
            [(None, getattr(func, 'genty_datasets', {}))],
            getattr(func, 'genty_dataproviders', []),
        )

        no_datasets = True
        for dataprovider, datasets in dataset_tuples:
            for dataset_name, dataset in six.iteritems(datasets):
                no_datasets = False
                yield name, func, dataset_name, dataset, dataprovider

        if no_datasets:
            # yield the original test method, unaltered
            yield name, func, None, None, None


def _expand_repeats(test_functions):
    """
    Generator producing test_methods, with any repeat count unrolled.

    :param test_functions:
        Sequence of tuples of
        - method_name      : Name of the test method
        - unbound function : Unbound function that will be the test method.
        - dataset name     : String representation of the given dataset
        - dataset          : Tuple representing the args for a test
        - param factory    : Function that returns params for the test method
    :type test_functions:
        `iterator` of `tuple` of
        (`unicode`, `function`, `unicode` or None, `tuple` or None, `function`)
    :return:
        Generator yielding a tuple of
        (method_name, unbound function, dataset, name dataset, repeat_suffix)
    :rtype:
        `generator` of `tuple` of (`unicode`, `function`,
        `unicode` or None, `tuple` or None, `function`, `unicode`)
    """
    for name, func, dataset_name, dataset, dataprovider in test_functions:
        repeat_count = getattr(func, 'genty_repeat_count', 0)
        if repeat_count:
            for i in range(1, repeat_count + 1):
                repeat_suffix = _build_repeat_suffix(i, repeat_count)
                yield (
                    name,
                    func,
                    dataset_name,
                    dataset,
                    dataprovider,
                    repeat_suffix,
                )
        else:
            yield name, func, dataset_name, dataset, dataprovider, None


def _add_new_test_methods(target_cls, tests_with_datasets_and_repeats):
    """Define the given tests in the given class.

    :param target_cls:
        Test class where to define the given test methods.
    :type target_cls:
        `class`
    :param tests_with_datasets_and_repeats:
        Sequence of tuples describing the new test to add to the class.
        (method_name, unbound function, dataset name, dataset,
         dataprovider, repeat_suffix)
    :type tests_with_datasets_and_repeats:
        Sequence of `tuple` of  (`unicode`, `function`,
        `unicode` or None, `tuple` or None, `function`, `unicode`)
    """
    for test_info in tests_with_datasets_and_repeats:
        (
            method_name,
            func,
            dataset_name,
            dataset,
            dataprovider,
            repeat_suffix,
        ) = test_info

        # Remove the original test_method as it's superseded by this
        # generated method.
        is_first_reference = _delete_original_test_method(
            target_cls,
            method_name,
        )

        # However, if that test_method is referenced by name in sys.argv
        # Then take 1 of the generated methods (we take the first) and
        # give that generated method the original name... so that the reference
        # can find an actual test method.
        if is_first_reference and _is_referenced_in_argv(method_name):
            dataset_name = None
            repeat_suffix = None

        _add_method_to_class(
            target_cls,
            method_name,
            func,
            dataset_name,
            dataset,
            dataprovider,
            repeat_suffix,
        )


def _is_referenced_in_argv(method_name):
    """
    Various test runners allow one to run a specific test like so:
        python -m unittest -v <test_module>.<test_name>

    Return True is the given method name is so referenced.

    :param method_name:
        Base name of the method to add.
    :type method_name:
        `unicode`
    :return:
        Is the given method referenced by the command line.
    :rtype:
        `bool`
    """
    expr = '.*[:.]{0}$'.format(method_name)
    regex = re.compile(expr)
    return any(regex.match(arg) for arg in sys.argv)


def _build_repeat_suffix(iteration, count):
    """
    Return the suffix string to identify iteration X out of Y.

    For example, with a count of 100, this will build strings like
    "iteration_053" or "iteration_008".

    :param iteration:
        Current iteration.
    :type iteration:
        `int`
    :param count:
        Total number of iterations.
    :type count:
        `int`
    :return:
        Repeat suffix.
    :rtype:
        `unicode`
    """
    format_width = int(math.ceil(math.log(count + 1, 10)))
    new_suffix = 'iteration_{0:0{width}d}'.format(
        iteration,
        width=format_width
    )
    return new_suffix


def _delete_original_test_method(target_cls, name):
    """
    Delete an original test method with the given name.

    :param target_cls:
        Target class.
    :type target_cls:
        `class`
    :param name:
        Name of the method to remove.
    :type name:
        `unicode`
    :return:
        True if the original method existed
    :rtype:
        `bool`
    """
    attribute = getattr(target_cls, name, None)
    if attribute and not getattr(attribute, 'genty_generated_test', None):
        try:
            delattr(target_cls, name)
        except AttributeError:
            pass
        return True
    else:
        return False


def _build_final_method_name(
        method_name,
        dataset_name,
        dataprovider_name,
        repeat_suffix,
):
    """
    Return a nice human friendly name, that almost looks like code.

    Example: a test called 'test_something' with a dataset of (5, 'hello')
         Return:  "test_something(5, 'hello')"

    Example: a test called 'test_other_stuff' with dataset of (9) and repeats
         Return: "test_other_stuff(9) iteration_<X>"

    :param method_name:
        Base name of the method to add.
    :type method_name:
        `unicode`
    :param dataset_name:
        Base name of the data set.
    :type dataset_name:
        `unicode` or None
    :param dataprovider_name:
        If there's a dataprovider involved, then this is its name.
    :type dataprovider_name:
        `unicode` or None
    :param repeat_suffix:
        Suffix to append to the name of the generated method.
    :type repeat_suffix:
        `unicode` or None
    :return:
        The fully composed name of the generated test method.
    :rtype:
        `unicode`
    """
    # For tests using a dataprovider, append "_<dataprovider_name>" to
    #  the test method name
    suffix = ''
    if dataprovider_name:
        suffix = '_{0}'.format(dataprovider_name)

    if not dataset_name and not repeat_suffix:
        return '{0}{1}'.format(method_name, suffix)

    if dataset_name:
        # Nosetest multi-processing code parses the full test name
        # to discern package/module names. Thus any periods in the test-name
        # causes that code to fail. So replace any periods with the unicode
        # middle-dot character. Yes, this change is applied independent
        # of the test runner being used... and that's fine since there is
        # no real contract as to how the fabricated tests are named.
        dataset_name = dataset_name.replace('.', REPLACE_FOR_PERIOD_CHAR)

    # Place data_set info inside parens, as if it were a function call
    suffix = '{0}({1})'.format(suffix, dataset_name or "")

    if repeat_suffix:
        suffix = '{0} {1}'.format(suffix, repeat_suffix)

    test_method_name_for_dataset = "{0}{1}".format(
        method_name,
        suffix,
    )

    return test_method_name_for_dataset


def _build_dataset_method(method, dataset):
    """
    Return a fabricated method that marshals the dataset into parameters
    for given 'method'
    :param method:
        The underlying test method.
    :type method:
        `callable`
    :param dataset:
        Tuple or GentyArgs instance containing the args of the dataset.
    :type dataset:
        `tuple` or :class:`GentyArgs`
    :return:
        Return an unbound function that will become a test method
    :rtype:
        `function`
    """
    if isinstance(dataset, GentyArgs):
        test_method = lambda my_self: method(
            my_self,
            *dataset.args,
            **dataset.kwargs
        )
    else:
        test_method = lambda my_self: method(
            my_self,
            *dataset
        )
    return test_method


def _build_dataprovider_method(method, dataset, dataprovider):
    """
    Return a fabricated method that calls the dataprovider with the given
    dataset, and marshals the return value from that into params to the
    underlying test 'method'.
    :param method:
        The underlying test method.
    :type method:
        `callable`
    :param dataset:
        Tuple or GentyArgs instance containing the args of the dataset.
    :type dataset:
        `tuple` or :class:`GentyArgs`
    :param dataprovider:
        The unbound function that's responsible for generating the actual
        params that will be passed to the test function.
    :type dataprovider:
        `callable`
    :return:
        Return an unbound function that will become a test method
    :rtype:
        `function`
    """
    if isinstance(dataset, GentyArgs):
        final_args = dataset.args
        final_kwargs = dataset.kwargs
    else:
        final_args = dataset
        final_kwargs = {}

    def test_method_wrapper(my_self):
        args = dataprovider(
            my_self,
            *final_args,
            **final_kwargs
        )

        kwargs = {}

        if isinstance(args, GentyArgs):
            kwargs = args.kwargs
            args = args.args
        elif not isinstance(args, (tuple, list)):
            args = (args, )

        return method(my_self, *args, **kwargs)

    return test_method_wrapper


def _build_test_method(method, dataset, dataprovider=None):
    """
    Return a fabricated method that marshals the dataset into parameters
    for given 'method'
    :param method:
        The underlying test method.
    :type method:
        `callable`
    :param dataset:
        Tuple or GentyArgs instance containing the args of the dataset.
    :type dataset:
        `tuple` or :class:`GentyArgs` or None
    :param dataprovider:
        The unbound function that's responsible for generating the actual
        params that will be passed to the test function. Can be None
    :type dataprovider:
        `callable` or None
    :return:
        Return an unbound function that will become a test method
    :rtype:
        `function`
    """
    if dataprovider:
        test_method = _build_dataprovider_method(method, dataset, dataprovider)
    elif dataset:
        test_method = _build_dataset_method(method, dataset)
    else:
        test_method = method
    return test_method


def _add_method_to_class(
        target_cls,
        method_name,
        func,
        dataset_name,
        dataset,
        dataprovider,
        repeat_suffix,
):
    """
    Add the described method to the given class.

    :param target_cls:
        Test class to which to add a method.
    :type target_cls:
        `class`
    :param method_name:
        Base name of the method to add.
    :type method_name:
        `unicode`
    :param func:
        The underlying test function to call.
    :type func:
        `callable`
    :param dataset_name:
        Base name of the data set.
    :type dataset_name:
        `unicode` or None
    :param dataset:
        Tuple containing the args of the dataset.
    :type dataset:
        `tuple` or None
    :param repeat_suffix:
        Suffix to append to the name of the generated method.
    :type repeat_suffix:
        `unicode` or None
    :param dataprovider:
        The unbound function that's responsible for generating the actual
        params that will be passed to the test function. Can be None.
    :type dataprovider:
        `callable`
    """
    # pylint: disable=too-many-arguments
    test_method_name_for_dataset = _build_final_method_name(
        method_name,
        dataset_name,
        dataprovider.__name__ if dataprovider else None,
        repeat_suffix,
    )

    test_method_for_dataset = _build_test_method(func, dataset, dataprovider)

    test_method_for_dataset = functools.update_wrapper(
        test_method_for_dataset,
        func,
    )

    test_method_name_for_dataset = encode_non_ascii_string(
        test_method_name_for_dataset,
    )
    test_method_for_dataset.__name__ = test_method_name_for_dataset
    test_method_for_dataset.genty_generated_test = True

    # Add the method to the class under the proper name
    setattr(target_cls, test_method_name_for_dataset, test_method_for_dataset)
