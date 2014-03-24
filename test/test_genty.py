# coding: utf-8

from __future__ import unicode_literals
import inspect
from unittest import TestCase
from mock import patch
from box.test.genty import genty
from box.test.genty import genty_dataset
from box.test.genty import genty_repeat
from box.test.genty.genty_args import genty_args


class GentyTest(TestCase):
    """Tests for :mod:`box.test.genty.genty`."""

    def _count_test_methods(self, target_cls):
        return len([
            name for name, _ in inspect.getmembers(target_cls, inspect.ismethod)
            if name.startswith('test')
        ])

    def test_genty_without_any_decorated_methods_is_a_no_op(self):
        @genty
        class some_class(object):
            def test_not_decorated(self):
                return 13

        self.assertEquals(13, some_class().test_not_decorated())

    def test_genty_ignores_non_test_methods(self):
        @genty
        class some_class(object):
            def random_method(self):
                return 'hi'

        self.assertEquals('hi', some_class().random_method())

    def test_genty_leaves_undecorated_tests_untouched(self):
        @genty
        class some_class(object):
            def test_undecorated(self):
                return 15

        self.assertEqual(15, some_class().test_undecorated())

    def test_genty_replicates_method_based_on_repeat_count(self):
        @genty
        class some_class(object):
            @genty_repeat(2)
            def test_repeat_decorated(self):
                return 13

        c = some_class()

        # The test method should be expanded twice and the original method should be gone.
        self.assertEqual(2, self._count_test_methods(some_class))
        getattr(c, 'test_repeat_decorated() iteration_1')()
        self.assertEqual(13, getattr(c, 'test_repeat_decorated() iteration_1')())
        self.assertEqual(13, getattr(c, 'test_repeat_decorated() iteration_2')())

        self.assertFalse(hasattr(c, 'test_repeat_decorated'), "original method should not exist")

    @patch('sys.argv', ['test_module.test_dot_argv', 'test_module:test_colon_argv'])
    def test_genty_generates_test_with_original_name_if_referenced_in_argv(self):

        @genty
        class some_class(object):
            @genty_repeat(3)
            def test_dot_argv(self):
                return 13

            @genty_dataset(10, 11)
            def test_colon_argv(self, arg):
                return 53

        c = some_class()

        # A test with the original same should exist, because of the argv reference.
        # And then the remaining generated tests exist as normal
        self.assertEqual(5, self._count_test_methods(some_class))
        self.assertEqual(13, c.test_dot_argv())
        self.assertEqual(13, getattr(c, 'test_dot_argv() iteration_2')())
        self.assertEqual(13, getattr(c, 'test_dot_argv() iteration_3')())

        self.assertEqual(53, c.test_colon_argv())
        self.assertEqual(53, getattr(c, 'test_colon_argv(11)')())

    def test_genty_formats_test_method_names_correctly_for_large_repeat_counts(self):
        @genty
        class some_class(object):
            @genty_repeat(100)
            def test_repeat_100(self):
                pass

        c = some_class()

        self.assertEqual(100, self._count_test_methods(some_class))
        for i in xrange(1, 10):
            self.assertTrue(hasattr(c, 'test_repeat_100() iteration_00{}'.format(i)))
        for i in xrange(10, 100):
            self.assertTrue(hasattr(c, 'test_repeat_100() iteration_0{}'.format(i)))
        self.assertTrue(hasattr(c, 'test_repeat_100() iteration_100'))

    def test_genty_properly_composes_dataset_methods(self):
        @genty
        class some_class(object):
            @genty_dataset(
                (100, 10),
                (200, 20),
                genty_args(110, 50),
                genty_args(x=120, y=80),
                genty_args(500, y=50),
                some_values=(250, 10),
                other_values=(300, 30),
                more_values=genty_args(400, y=40)
            )
            def test_something(self, x, y):
                return x + y + 1

        c = some_class()

        self.assertEqual(8, self._count_test_methods(some_class))
        self.assertEqual(111, getattr(c, 'test_something(100, 10)')())
        self.assertEqual(221, getattr(c, 'test_something(200, 20)')())
        self.assertEqual(161, getattr(c, 'test_something(110, 50)')())
        self.assertEqual(201, getattr(c, 'test_something(x=120, y=80)')())
        self.assertEqual(551, getattr(c, 'test_something(500, y=50)')())
        self.assertEqual(261, getattr(c, 'test_something(some_values)')())
        self.assertEqual(331, getattr(c, 'test_something(other_values)')())
        self.assertEqual(441, getattr(c, 'test_something(more_values)')())

        self.assertFalse(hasattr(c, 'test_something'), "original method should not exist")

    def test_genty_properly_composes_dataset_methods_up_hierarchy(self):
        @genty
        class some_parent(object):
            @genty_dataset(100, 10)
            def test_parent(self, x):
                return x + 1

        @genty
        class some_child(some_parent):
            @genty_dataset('a', 'b')
            def test_child(self, x):
                return x + x

        c = some_child()

        self.assertEqual(4, self._count_test_methods(some_child))
        self.assertEqual(101, getattr(c, 'test_parent(100)')())
        self.assertEqual(11, getattr(c, 'test_parent(10)')())
        self.assertEqual('aa', getattr(c, "test_child(u'a')")())
        self.assertEqual('bb', getattr(c, "test_child(u'b')")())

        self.assertFalse(hasattr(c, 'test_parent'), "original method should not exist")
        self.assertFalse(hasattr(c, 'test_child'), "original method should not exist")

    def test_genty_properly_composes_repeat_methods_up_hierarchy(self):
        @genty
        class some_parent(object):
            @genty_repeat(3)
            def test_parent(self):
                return 1 + 1

        @genty
        class some_child(some_parent):
            @genty_repeat(2)
            def test_child(self):
                return 'r'

        c = some_child()

        self.assertEqual(5, self._count_test_methods(some_child))

        self.assertEqual(2, getattr(c, 'test_parent() iteration_1')())
        self.assertEqual(2, getattr(c, 'test_parent() iteration_2')())
        self.assertEqual(2, getattr(c, 'test_parent() iteration_3')())
        self.assertEqual('r', getattr(c, 'test_child() iteration_1')())
        self.assertEqual('r', getattr(c, 'test_child() iteration_2')())

        self.assertFalse(hasattr(c, 'test_parent'), "original method should not exist")
        self.assertFalse(hasattr(c, 'test_child'), "original method should not exist")

    def test_genty_replicates_method_with_repeat_then_dataset_decorators(self):
        @genty
        class some_class(object):
            @genty_repeat(2)
            @genty_dataset('first', 'second')
            def test_repeat_and_dataset(self, x):
                return x + x

        c = some_class()

        # The test method should be expanded twice and the original method should be gone.
        self.assertEqual(4, self._count_test_methods(some_class))
        self.assertEqual('firstfirst', getattr(c, "test_repeat_and_dataset(u'first') iteration_1")())
        self.assertEqual('firstfirst', getattr(c, "test_repeat_and_dataset(u'first') iteration_2")())
        self.assertEqual('secondsecond', getattr(c, "test_repeat_and_dataset(u'second') iteration_1")())
        self.assertEqual('secondsecond', getattr(c, "test_repeat_and_dataset(u'second') iteration_2")())

        self.assertFalse(hasattr(c, 'test_repeat_and_dataset'), "original method should not exist")

    def test_genty_replicates_method_with_dataset_then_repeat_decorators(self):
        @genty
        class some_class(object):
            @genty_dataset(11, 22)
            @genty_repeat(2)
            def test_repeat_and_dataset(self, x):
                return x + 13

        c = some_class()

        # The test method should be expanded twice and the original method should be gone.
        self.assertEqual(4, self._count_test_methods(some_class))
        self.assertEqual(24, getattr(c, 'test_repeat_and_dataset(11) iteration_1')())
        self.assertEqual(24, getattr(c, 'test_repeat_and_dataset(11) iteration_2')())
        self.assertEqual(35, getattr(c, 'test_repeat_and_dataset(22) iteration_1')())
        self.assertEqual(35, getattr(c, 'test_repeat_and_dataset(22) iteration_2')())

        self.assertFalse(hasattr(c, 'test_repeat_and_dataset'), "original method should not exist")

    def test_genty_properly_composes_method_with_non_ascii_chars_in_dataset_name(self):
        @genty
        class some_class(object):
            @genty_dataset(' Pȅtȅr', 'wow 漢字')
            def test_unicode(self, x):
                return 33

        c = some_class()

        self.assertEqual(
            33,
            getattr(c, 'test_unicode({})'.format(repr(' Pȅtȅr')).encode('utf-8', 'replace'))()
        )

        self.assertEqual(
            33,
            getattr(c, 'test_unicode({})'.format(repr('wow 漢字')).encode('utf-8', 'replace'))()
        )

    def test_genty_properly_composes_method_with_special_chars_in_dataset_name(self):
        @genty
        class some_class(object):
            @genty_dataset(*'!"#$%&\'()*.+-/:;>=<?@[\]^_`{|}~,')
            def test_unicode(self, x):
                return 33

        instance = some_class()

        for char in '!"#$%&\'()*.+-/:;>=<?@[\]^_`{|}~,':
            self.assertEqual(
                33,
                getattr(instance, 'test_unicode({})'.format(repr(char)))()
            )
