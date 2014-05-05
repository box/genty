# coding: utf-8

from __future__ import unicode_literals
import inspect
from unittest import TestCase
from mock import patch
from genty import genty, genty_dataset, genty_args, genty_repeat


class GentyTest(TestCase):
    """Tests for :mod:`box.test.genty.genty`."""
    # pylint: disable=no-self-use
    # Lots of the tests below create dummy methods that don't use 'self'.

    def _count_test_methods(self, target_cls):
        return len([
            name for name, _ in inspect.getmembers(target_cls, inspect.ismethod)
            if name.startswith('test')
        ])

    def test_genty_without_any_decorated_methods_is_a_no_op(self):
        @genty
        class SomeClass(object):
            def test_not_decorated(self):
                return 13

        self.assertEquals(13, SomeClass().test_not_decorated())

    def test_genty_ignores_non_test_methods(self):
        @genty
        class SomeClass(object):
            def random_method(self):
                return 'hi'

        self.assertEquals('hi', SomeClass().random_method())

    def test_genty_leaves_undecorated_tests_untouched(self):
        @genty
        class SomeClass(object):
            def test_undecorated(self):
                return 15

        self.assertEqual(15, SomeClass().test_undecorated())

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
        for i in xrange(1, 10):
            self.assertTrue(hasattr(instance, 'test_repeat_100() iteration_00{}'.format(i)))
        for i in xrange(10, 100):
            self.assertTrue(hasattr(instance, 'test_repeat_100() iteration_0{}'.format(i)))
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
        @genty
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
        self.assertEqual('aa', getattr(instance, "test_child(u'a')")())
        self.assertEqual('bb', getattr(instance, "test_child(u'b')")())

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
        self.assertEqual('firstfirst', getattr(instance, "test_repeat_and_dataset(u'first') iteration_1")())
        self.assertEqual('firstfirst', getattr(instance, "test_repeat_and_dataset(u'first') iteration_2")())
        self.assertEqual('secondsecond', getattr(instance, "test_repeat_and_dataset(u'second') iteration_1")())
        self.assertEqual('secondsecond', getattr(instance, "test_repeat_and_dataset(u'second') iteration_2")())

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
            getattr(instance, 'test_unicode({})'.format(repr(' Pȅtȅr')).encode('utf-8', 'replace'))()
        )

        self.assertEqual(
            33,
            getattr(instance, 'test_unicode({})'.format(repr('wow 漢字')).encode('utf-8', 'replace'))()
        )

    def test_genty_properly_composes_method_with_special_chars_in_dataset_name(self):
        @genty
        class SomeClass(object):
            @genty_dataset(*r'!"#$%&\'()*.+-/:;>=<?@[\]^_`{|}~,')
            def test_unicode(self, _):
                return 33

        instance = SomeClass()

        for char in r'!"#$%&\'()*.+-/:;>=<?@[\]^_`{|}~,':
            self.assertEqual(
                33,
                getattr(instance, 'test_unicode({})'.format(repr(char)))()
            )
