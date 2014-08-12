# coding: utf-8

from __future__ import unicode_literals
import functools
import math
import types
import re
import sys
from box.test.genty.genty_args import GentyArgs


def genty(target_cls):
    """Decorator used in conjunction with @genty_dataset and @genty_repeat.

    This decorator takes the information provided by @genty_dataset and
    @genty_repeat and generates the corresponding test methods.

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
    entries = dict(target_cls.__dict__.iteritems())
    for key, value in entries.iteritems():
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
        (method_name, unbound function, dataset name, dataset)
    :rtype:
        `generator` of `tuple` of
        (`unicode`, `function`, `unicode` or None, `tuple` or None)
    """
    for name, func in test_functions:
        datasets = getattr(func, 'genty_datasets', {})
        if datasets:
            for dataset_name, dataset in datasets.iteritems():
                yield name, func, dataset_name, dataset
        else:
            yield name, func, None, None


def _expand_repeats(test_functions):
    """
    Generator producing test_methods, with any repeat count unrolled.

    :param test_functions:
        Sequence of tuples of
        (test_method_name, test unbound function, dataset name, dataset)
    :type test_functions:
        `iterator` of `tuple` of
        (`unicode`, `function`, `unicode` or None, `tuple` or None)
    :return:
        Generator yielding a tuple of
        (method_name, unbound function, dataset, name dataset, repeat_suffix)
    :rtype:
        `generator` of `tuple` of (`unicode`, `function`,
        `unicode` or None, `tuple` or None, `unicode`)
    """
    for name, func, dataset_name, dataset in test_functions:
        repeat_count = getattr(func, 'genty_repeat_count', 0)
        if repeat_count:
            for i in xrange(1, repeat_count + 1):
                repeat_suffix = _build_repeat_suffix(i, repeat_count)
                yield name, func, dataset_name, dataset, repeat_suffix
        elif dataset:
            yield name, func, dataset_name, dataset, None


def _add_new_test_methods(target_cls, tests_with_datasets_and_repeats):
    """Define the given tests in the given class.

    :param target_cls:
        Test class where to define the given test methods.
    :type target_cls:
        `class`
    :param tests_with_datasets_and_repeats:
        Sequence of tuples describing the new test to add to the class.
        (method_name, unbound function, dataset name, dataset , repeat_suffix)
    :type tests_with_datasets_and_repeats:
        Sequence of `tuple` of  (`unicode`, `function`,
        `unicode` or None, `tuple` or None, `unicode`)
    """
    for test_info in tests_with_datasets_and_repeats:
        method_name, func, dataset_name, dataset, repeat_suffix = test_info

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
    expr = '.*[:.]{}$'.format(method_name)
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
    new_suffix = 'iteration_{:0{width}d}'.format(iteration, width=format_width)
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
        delattr(target_cls, name)
        return True
    else:
        return False


def _build_final_method_name(method_name, dataset_name, repeat_suffix):
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
    :param repeat_suffix:
        Suffix to append to the name of the generated method.
    :type repeat_suffix:
        `unicode` or None
    :return:
        The fully composed name of the generated test method.
    :rtype:
        `unicode`
    """
    if not dataset_name and not repeat_suffix:
        return method_name

    # Place data_set info inside parens, as if it were a function call
    test_method_suffix = '({})'.format(dataset_name or "")

    if repeat_suffix:
        test_method_suffix = test_method_suffix + " " + repeat_suffix

    test_method_name_for_dataset = "{}{}".format(
        method_name,
        test_method_suffix,
    )

    return test_method_name_for_dataset


def _build_method_wrapper(method, dataset):
    if dataset:
        # Create the test method with the given data set.
        if isinstance(dataset, GentyArgs):
            test_method_for_dataset = lambda my_self: method(
                my_self,
                *dataset.args,
                **dataset.kwargs
            )
        else:
            test_method_for_dataset = lambda my_self: method(my_self, *dataset)
    else:
        test_method_for_dataset = lambda my_self: method(my_self)
    return test_method_for_dataset


def _add_method_to_class(
        target_cls,
        method_name,
        func,
        dataset_name,
        dataset,
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
        The test function to add.
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
    """
    test_method_name_for_dataset = _build_final_method_name(
        method_name,
        dataset_name,
        repeat_suffix,
    )

    test_method_for_dataset = _build_method_wrapper(func, dataset)

    test_method_for_dataset = functools.update_wrapper(
        test_method_for_dataset,
        func,
    )

    test_method_name_for_dataset = test_method_name_for_dataset.encode(
        'utf-8',
        'replace',
    )
    test_method_for_dataset.__name__ = test_method_name_for_dataset
    test_method_for_dataset.genty_generated_test = True

    # Add the method to the class under the proper name
    setattr(target_cls, test_method_name_for_dataset, test_method_for_dataset)
