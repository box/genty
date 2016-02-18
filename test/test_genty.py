# coding: utf-8

from __future__ import unicode_literals
import functools
import inspect
from mock import patch
import six
from genty import genty, genty_args, genty_dataset, genty_repeat, genty_dataprovider
from genty.genty import REPLACE_FOR_PERIOD_CHAR
from genty.private import encode_non_ascii_string
from test.test_case_base import TestCase


class GentyTest(TestCase):
    """Tests for :mod:`box.test.genty.genty`."""
    # pylint: disable=no-self-use
    # Lots of the tests below create dummy methods that don't use 'self'.

    def _count_test_methods(self, target_cls):
        method_filter = inspect.ismethod if six.PY2 else inspect.isfunction
        return len([
            name for name, _ in inspect.getmembers(target_cls, method_filter)
            if name.startswith('test')
        ])

    def test_genty_without_any_decorated_methods_is_a_no_op(self):
        @genty
        class SomeClass(object):
            def test_not_decorated(self):
                return 13

        self.assertEqual(13, SomeClass().test_not_decorated())

    def test_genty_ignores_non_test_methods(self):
        @genty
        class SomeClass(object):
            def random_method(self):
                return 'hi'

        self.assertEqual('hi', SomeClass().random_method())

    def test_genty_leaves_undecorated_tests_untouched(self):
        @genty
        class SomeClass(object):
            def test_undecorated(self):
                return 15

        self.assertEqual(15, SomeClass().test_undecorated())

    def test_genty_decorates_test_with_args(self):
        @genty
        class SomeClass(object):
            @genty_dataset((4, 7))
            def test_decorated(self, aval, bval):
                return aval + bval

        instance = SomeClass()
        self.assertEqual(11, getattr(instance, 'test_decorated(4, 7)')())

    def test_genty_decorates_with_dataprovider_args(self):
        @genty
        class SomeClass(object):
            @genty_dataset((7, 4))
            def my_param_factory(self, first, second):
                return first + second, first - second, max(first, second)

            @genty_dataprovider(my_param_factory)
            def test_decorated(self, summation, difference, maximum):
                return summation, difference, maximum

        instance = SomeClass()
        self.assertEqual(
            (11, 3, 7),
            getattr(
                instance,
                'test_decorated_{0}(7, 4)'.format('my_param_factory'),
            )(),
        )

    def test_genty_dataprovider_can_handle_single_parameter(self):
        @genty
        class SomeClass(object):
            @genty_dataset((7, 4))
            def my_param_factory(self, first, second):
                return first + second

            @genty_dataprovider(my_param_factory)
            def test_decorated(self, sole_arg):
                return sole_arg

        instance = SomeClass()
        self.assertEqual(
            11,
            getattr(
                instance,
                'test_decorated_{0}(7, 4)'.format('my_param_factory'),
            )(),
        )

    def test_genty_dataprovider_doesnt_need_any_datasets(self):
        @genty
        class SomeClass(object):
            def my_param_factory(self):
                return 101

            @genty_dataprovider(my_param_factory)
            def test_decorated(self, sole_arg):
                return sole_arg

        instance = SomeClass()
        self.assertEqual(
            101,
            getattr(
                instance,
                'test_decorated_{0}'.format('my_param_factory'),
            )(),
        )

    def test_genty_dataprovider_can_be_chained(self):
        @genty
        class SomeClass(object):
            @genty_dataset((7, 4))
            def my_param_factory(self, first, second):
                return first + second, first - second, max(first, second)

            @genty_dataset(3, 5)
            def another_param_factory(self, only):
                return only + only, only - only, (only * only)

            @genty_dataprovider(my_param_factory)
            @genty_dataprovider(another_param_factory)
            def test_decorated(self, value1, value2, value3):
                return value1, value2, value3

        instance = SomeClass()
        self.assertEqual(
            (11, 3, 7),
            getattr(
                instance,
                'test_decorated_{0}(7, 4)'.format('my_param_factory'),
            )(),
        )
        self.assertEqual(
            (6, 0, 9),
            getattr(
                instance,
                'test_decorated_{0}(3)'.format('another_param_factory'),
            )(),
        )
        self.assertEqual(
            (10, 0, 25),
            getattr(
                instance,
                'test_decorated_{0}(5)'.format('another_param_factory'),
            )(),
        )

    def test_dataprovider_args_can_use_genty_args(self):
        @genty
        class SomeClass(object):
            @genty_dataset(
                genty_args(second=5, first=15),
            )
            def my_param_factory(self, first, second):
                return first + second, first - second, max(first, second)

            @genty_dataprovider(my_param_factory)
            def test_decorated(self, summation, difference, maximum):
                return summation, difference, maximum

        instance = SomeClass()
        self.assertEqual(
            (20, 10, 15),
            getattr(
                instance,
                'test_decorated_{0}(first=15, second=5)'.format('my_param_factory'),
            )(),
        )

    def test_dataproviders_and_datasets_can_mix(self):
        @genty
        class SomeClass(object):
            @genty_dataset((7, 4))
            def my_param_factory(self, first, second):
                return first + second, first - second

            @genty_dataprovider(my_param_factory)
            @genty_dataset((7, 4), (11, 3))
            def test_decorated(self, param1, param2):
                return param1, param1, param2, param2

        instance = SomeClass()
        self.assertEqual(
            (11, 11, 3, 3),
            getattr(
                instance,
                'test_decorated_{0}(7, 4)'.format('my_param_factory'),
            )(),
        )
        self.assertEqual(
            (7, 7, 4, 4),
            getattr(instance, 'test_decorated(7, 4)')(),
        )
        self.assertEqual(
            (11, 11, 3, 3),
            getattr(instance, 'test_decorated(11, 3)')(),
        )

    def test_genty_replicates_method_based_on_repeat_count(self):
        @genty
        class SomeClass(object):
            @genty_repeat(2)
            def test_repeat_decorated(self):
                return 13

        instance = SomeClass()

        # The test method should be expanded twice and the original method should be gone.
        self.assertEqual(2, self._count_test_methods(SomeClass))
        getattr(instance, 'test_repeat_decorated() iteration_1')()
        self.assertEqual(13, getattr(instance, 'test_repeat_decorated() iteration_1')())
        self.assertEqual(13, getattr(instance, 'test_repeat_decorated() iteration_2')())

        self.assertFalse(hasattr(instance, 'test_repeat_decorated'), "original method should not exist")

    @patch('sys.argv', ['test_module.test_dot_argv', 'test_module:test_colon_argv'])
    def test_genty_generates_test_with_original_name_if_referenced_in_argv(self):

        @genty
        class SomeClass(object):
            @genty_repeat(3)
            def test_dot_argv(self):
                return 13

            @genty_dataset(10, 11)
            def test_colon_argv(self, _):
                return 53

        instance = SomeClass()

        # A test with the original same should exist, because of the argv reference.
        # And then the remaining generated tests exist as normal
        self.assertEqual(5, self._count_test_methods(SomeClass))
        self.assertEqual(13, instance.test_dot_argv())
        self.assertEqual(13, getattr(instance, 'test_dot_argv() iteration_2')())
        self.assertEqual(13, getattr(instance, 'test_dot_argv() iteration_3')())

        # pylint: disable=no-value-for-parameter
        # genty replace the original 'test_colon_argv' method with one that doesn't
        # take any paramteres. Hence pylint's confusion
        self.assertEqual(53, instance.test_colon_argv())
        # pylint: enable=no-value-for-parameter
        self.assertEqual(53, getattr(instance, 'test_colon_argv(11)')())

    def test_genty_formats_test_method_names_correctly_for_large_repeat_counts(self):
        @genty
        class SomeClass(object):
            @genty_repeat(100)
            def test_repeat_100(self):
                pass

        instance = SomeClass()

        self.assertEqual(100, self._count_test_methods(SomeClass))
        for i in range(1, 10):
            self.assertTrue(hasattr(instance, 'test_repeat_100() iteration_00{0}'.format(i)))
        for i in range(10, 100):
            self.assertTrue(hasattr(instance, 'test_repeat_100() iteration_0{0}'.format(i)))
        self.assertTrue(hasattr(instance, 'test_repeat_100() iteration_100'))

    def test_genty_properly_composes_dataset_methods(self):
        @genty
        class SomeClass(object):
            @genty_dataset(
                (100, 10),
                (200, 20),
                genty_args(110, 50),
                genty_args(val=120, other=80),
                genty_args(500, other=50),
                some_values=(250, 10),
                other_values=(300, 30),
                more_values=genty_args(400, other=40)
            )
            def test_something(self, val, other):
                return val + other + 1

        instance = SomeClass()

        self.assertEqual(8, self._count_test_methods(SomeClass))
        self.assertEqual(111, getattr(instance, 'test_something(100, 10)')())
        self.assertEqual(221, getattr(instance, 'test_something(200, 20)')())
        self.assertEqual(161, getattr(instance, 'test_something(110, 50)')())
        self.assertEqual(201, getattr(instance, 'test_something(other=80, val=120)')())
        self.assertEqual(551, getattr(instance, 'test_something(500, other=50)')())
        self.assertEqual(261, getattr(instance, 'test_something(some_values)')())
        self.assertEqual(331, getattr(instance, 'test_something(other_values)')())
        self.assertEqual(441, getattr(instance, 'test_something(more_values)')())

        self.assertFalse(hasattr(instance, 'test_something'), "original method should not exist")

    def test_genty_properly_composes_dataset_methods_up_hierarchy(self):
        # Some test frameworks set attributes on test classes directly through metaclasses. pymox is an example.
        # This test ensures that genty still won't expand inherited tests twice.
        class SomeMeta(type):
            def __init__(cls, name, bases, d):
                for base in bases:
                    for attr_name in dir(base):
                        if attr_name not in d:
                            d[attr_name] = getattr(base, attr_name)

                for func_name, func in d.items():
                    if func_name.startswith('test') and callable(func):
                        setattr(cls, func_name, cls.wrap_method(func))

                # pylint:disable=bad-super-call
                super(SomeMeta, cls).__init__(name, bases, d)

            def wrap_method(cls, func):
                @functools.wraps(func)
                def wrapped(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapped

        @genty
        @six.add_metaclass(SomeMeta)
        class SomeParent(object):
            @genty_dataset(100, 10)
            def test_parent(self, val):
                return val + 1

        @genty
        class SomeChild(SomeParent):
            @genty_dataset('a', 'b')
            def test_child(self, val):
                return val + val

        instance = SomeChild()

        self.assertEqual(4, self._count_test_methods(SomeChild))
        self.assertEqual(101, getattr(instance, 'test_parent(100)')())
        self.assertEqual(11, getattr(instance, 'test_parent(10)')())
        self.assertEqual('aa', getattr(instance, "test_child({0})".format(repr('a')))())
        self.assertEqual('bb', getattr(instance, "test_child({0})".format(repr('b')))())

        entries = dict(six.iteritems(SomeChild.__dict__))
        self.assertEqual(4, len([meth for name, meth in six.iteritems(entries) if name.startswith('test')]))
        self.assertFalse(hasattr(instance, 'test_parent(100)(100)'), 'genty should not expand a test more than once')
        self.assertFalse(hasattr(instance, 'test_parent(100)(10)'), 'genty should not expand a test more than once')
        self.assertFalse(hasattr(instance, 'test_parent(100)(10)'), 'genty should not expand a test more than once')
        self.assertFalse(hasattr(instance, 'test_parent(10)(10)'), 'genty should not expand a test more than once')

        self.assertFalse(hasattr(instance, 'test_parent'), "original method should not exist")
        self.assertFalse(hasattr(instance, 'test_child'), "original method should not exist")

    def test_genty_properly_composes_repeat_methods_up_hierarchy(self):
        @genty
        class SomeParent(object):
            @genty_repeat(3)
            def test_parent(self):
                return 1 + 1

        @genty
        class SomeChild(SomeParent):
            @genty_repeat(2)
            def test_child(self):
                return 'r'

        instance = SomeChild()

        self.assertEqual(5, self._count_test_methods(SomeChild))

        self.assertEqual(2, getattr(instance, 'test_parent() iteration_1')())
        self.assertEqual(2, getattr(instance, 'test_parent() iteration_2')())
        self.assertEqual(2, getattr(instance, 'test_parent() iteration_3')())
        self.assertEqual('r', getattr(instance, 'test_child() iteration_1')())
        self.assertEqual('r', getattr(instance, 'test_child() iteration_2')())

        self.assertFalse(hasattr(instance, 'test_parent'), "original method should not exist")
        self.assertFalse(hasattr(instance, 'test_child'), "original method should not exist")

    def test_genty_replicates_method_with_repeat_then_dataset_decorators(self):
        @genty
        class SomeClass(object):
            @genty_repeat(2)
            @genty_dataset('first', 'second')
            def test_repeat_and_dataset(self, val):
                return val + val

        instance = SomeClass()

        # The test method should be expanded twice and the original method should be gone.
        self.assertEqual(4, self._count_test_methods(SomeClass))
        self.assertEqual('firstfirst', getattr(instance, "test_repeat_and_dataset({0}) iteration_1".format(repr('first')))())
        self.assertEqual('firstfirst', getattr(instance, "test_repeat_and_dataset({0}) iteration_2".format(repr('first')))())
        self.assertEqual('secondsecond', getattr(instance, "test_repeat_and_dataset({0}) iteration_1".format(repr('second')))())
        self.assertEqual('secondsecond', getattr(instance, "test_repeat_and_dataset({0}) iteration_2".format(repr('second')))())

        self.assertFalse(hasattr(instance, 'test_repeat_and_dataset'), "original method should not exist")

    def test_genty_replicates_method_with_dataset_then_repeat_decorators(self):
        @genty
        class SomeClass(object):
            @genty_dataset(11, 22)
            @genty_repeat(2)
            def test_repeat_and_dataset(self, val):
                return val + 13

        instance = SomeClass()

        # The test method should be expanded twice and the original method should be gone.
        self.assertEqual(4, self._count_test_methods(SomeClass))
        self.assertEqual(24, getattr(instance, 'test_repeat_and_dataset(11) iteration_1')())
        self.assertEqual(24, getattr(instance, 'test_repeat_and_dataset(11) iteration_2')())
        self.assertEqual(35, getattr(instance, 'test_repeat_and_dataset(22) iteration_1')())
        self.assertEqual(35, getattr(instance, 'test_repeat_and_dataset(22) iteration_2')())

        self.assertFalse(hasattr(instance, 'test_repeat_and_dataset'), "original method should not exist")

    def test_genty_properly_composes_method_with_non_ascii_chars_in_dataset_name(self):
        @genty
        class SomeClass(object):
            @genty_dataset(' Pȅtȅr', 'wow 漢字')
            def test_unicode(self, _):
                return 33

        instance = SomeClass()

        self.assertEqual(
            33,
            getattr(instance, encode_non_ascii_string('test_unicode({0})'.format(repr(' Pȅtȅr'))))()
        )

        self.assertEqual(
            33,
            getattr(instance, encode_non_ascii_string('test_unicode({0})'.format(repr('wow 漢字'))))()
        )

    def test_genty_properly_composes_method_with_special_chars_in_dataset_name(self):
        @genty
        class SomeClass(object):
            @genty_dataset(*r'!"#$%&\'()*+-/:;>=<?@[\]^_`{|}~,')
            def test_unicode(self, _):
                return 33

        instance = SomeClass()

        for char in r'!"#$%&\'()*+-/:;>=<?@[\]^_`{|}~,':
            self.assertEqual(
                33,
                getattr(instance, 'test_unicode({0})'.format(repr(char)))()
            )

    def test_genty_replaces_standard_period_with_middle_dot(self):
        # The nosetest multi-processing code parses the full test name
        # to discern package/module names. Thus any periods in the test-name
        # causes that code to fail. This test verifies that periods are replaced
        # with the unicode middle-dot character.
        @genty
        class SomeClass(object):
            @genty_dataset('a.b.c')
            def test_period_char(self, _):
                return 33

        instance = SomeClass()

        for attr in dir(instance):
            if attr.startswith(encode_non_ascii_string('test_period_char')):
                self.assertNotIn(
                    encode_non_ascii_string('.'),
                    attr,
                    "didn't expect a period character",
                )
                self.assertIn(
                    encode_non_ascii_string(REPLACE_FOR_PERIOD_CHAR),
                    attr,
                    "expected the middle-dot replacement character",
                )
                break
        else:
            raise KeyError("failed to find the expected test")

    def test_genty_properly_calls_patched_methods(self):
        class PatchableClass(object):
            @staticmethod
            def my_method(num):
                return num + 1

        @genty
        class SomeClass(object):
            @genty_dataset(42)
            @patch.object(PatchableClass, 'my_method')
            def test_patched_method(self, num, mocked_method):
                mocked_method.return_value = num + 2
                return PatchableClass.my_method(num)

            @genty_dataset(42)
            def test_unpatched_method(self, num):
                return PatchableClass.my_method(num)

        instance = SomeClass()
        patched_method = getattr(instance, 'test_patched_method(42)')
        unpatched_method = getattr(instance, 'test_unpatched_method(42)')
        self.assertEqual(44, patched_method())
        self.assertEqual(43, unpatched_method())

    def test_genty_does_not_fail_when_trying_to_delete_attribute_defined_on_metaclass(self):
        class SomeMeta(type):
            def __new__(mcs, name, bases, attributes):
                attributes['test_defined_in_metaclass'] = genty_dataset('foo')(mcs.test_defined_in_metaclass)
                # pylint:disable=bad-super-call
                generated_class = super(SomeMeta, mcs).__new__(mcs, name, bases, attributes)
                return generated_class

            @staticmethod
            def test_defined_in_metaclass():
                pass

        @genty
        @six.add_metaclass(SomeMeta)
        class SomeClass(object):
            pass

        instance = SomeClass()

        self.assertIn('test_defined_in_metaclass({0})'.format(repr('foo')), dir(instance))

    def test_dataprovider_returning_genty_args_passes_correct_args(self):
        @genty
        class TestClass(object):
            def builder(self):
                return genty_args(42, named='named_arg')

            @genty_dataprovider(builder)
            def test_method(self, number, default=None, named=None):
                return number, default, named

        instance = TestClass()
        # pylint:disable=no-member
        self.assertItemsEqual((42, None, 'named_arg'), instance.test_method_builder())
