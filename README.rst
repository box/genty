genty
=====

.. image:: http://opensource.box.com/badges/active.svg
    :target: http://opensource.box.com/badges

.. image:: https://travis-ci.org/box/genty.png?branch=master
    :target: https://travis-ci.org/box/genty

.. image:: https://img.shields.io/pypi/v/genty.svg
    :target: https://pypi.python.org/pypi/genty

.. image:: https://img.shields.io/pypi/dm/genty.svg
    :target: https://pypi.python.org/pypi/genty


About
-----

Genty, pronounced "gen-tee", stands for "generate tests". It promotes generative 
testing, where a single test can execute over a variety of input. Genty makes
this a breeze.

For example, consider a file sample.py containing both the code under test and
the tests:

.. code-block:: python

    from genty import genty, genty_repeat, genty_dataset
    from unittest import TestCase

    # Here's the class under test
    class MyClass(object):
        def add_one(self, x): 
            return x + 1

    # Here's the test code
    @genty
    class MyClassTests(TestCase):
        @genty_dataset(
            (0, 1),
            (100000, 100001),
        )
        def test_add_one(self, value, expected_result):
            actual_result = MyClass().add_one(value)
            self.assertEqual(expected_result, actual_result)


Running the ``MyClassTests`` using the default unittest runner

.. code-block:: console

    $ python -m unittest -v sample
    test_add_one(0, 1) (sample.MyClassTests) ... ok
    test_add_one(100000, 100001) (sample.MyClassTests) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

Instead of having to write multiple independent tests for various test cases, 
code can be refactored and parametrized using genty!

It produces readable tests.
It produces maintainable tests.
It produces expressive tests.

Another option is running the same test multiple times. This is useful in stress
tests or when exercising code looking for race conditions. This particular test

.. code-block:: python

    @genty_repeat(3)
    def test_adding_one_to_zero(self):
        self.assertEqual(1, MyClass().add_one(0))


would be run 3 times, producing output like

.. code-block:: console

    $ python -m unittest -v sample
    test_adding_one() iteration_1 (sample.MyClassTests) ... ok
    test_adding_one() iteration_2 (sample.MyClassTests) ... ok
    test_adding_one() iteration_3 (sample.MyClassTests) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 0.001s

    OK

The 2 techniques can be combined:

.. code-block:: python

        @genty_repeat(2)
        @genty_dataset(
            (0, 1),
            (100000, 100001),
        )
        def test_add_one(self, value, expected_result):
            actual_result = MyClass().add_one(value)
            self.assertEqual(expected_result, actual_result)
            

There are more options to explore including naming your datasets and ``genty_args``.

.. code-block:: python
 
        @genty_dataset(
            default_case=(0, 1),
            limit_case=(999, 1000),
            error_case=genty_args(-1, -1, is_something=False),
        )
        def test_complex(self, value1, value2, optional_value=None, is_something=True):
            ...
 

would run 3 tests, producing output like

.. code-block:: console

    $ python -m unittest -v sample
    test_complex(default_case) (sample.MyClassTests) ... ok
    test_complex(limit_case) (sample.MyClassTests) ... ok
    test_complex(error_case) (sample.MyClassTests) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 0.003s

    OK


The ``@genty_datasets`` can be chained together. This is useful, for example, if there are semantically different datasets
so keeping them separate would help expressiveness.


.. code-block:: python

	@genty_dataset(10, 100)
	@genty_dataset('first', 'second')
	def test_composing(self, parameter_value):
		...


would run 4 tests, producing output like

.. code-block:: console

    $ python -m unittest -v sample
    test_composing(10) (sample.MyClassTests) ... ok
    test_composing(100) (sample.MyClassTests) ... ok
    test_composing(u'first') (sample.MyClassTests) ... ok
    test_composing(u'second') (sample.MyClassTests) ... ok

    ----------------------------------------------------------------------
    Ran 4 tests in 0.000s

    OK


Sometimes the parameters to a test can't be determined at module load time. For example,
some test might be based on results from some http request. And first the test needs to
authenticate, etc. This is supported using the ``@genty_dataprovider`` decorator like so:


.. code-block:: python

    def setUp(self):
        super(MyClassTests, self).setUp()
        
        # http authentication happens
        # And imagine that _some_function is actually some http request
        self._some_function = lambda x, y: ((x + y), (x - y), (x * y))

    @genty_dataset((1000, 100), (100, 1))
    def calculate(self, x_val, y_val):
        # when this is called... we've been authenticated
        return self._some_function(x_val, y_val)

    @genty_dataprovider(calculate)
    def test_heavy(self, data1, data2, data3):
        ...


would run 4 tests, producing output like

.. code-block:: console


	$ python -m unittest -v sample
	test_heavy_calculate(100, 1) (sample.MyClassTests) ... ok
	test_heavy_calculate(1000, 100) (sample.MyClassTests) ... ok

	----------------------------------------------------------------------
	Ran 2 tests in 0.000s

	OK

Notice here how the name of the helper (``calculate``) is added to the names of the 2
executed test cases.

Like ``@genty_dataset``, ``@genty_dataprovider`` can be chained together.

Enjoy!

Deferred Parameterization
-------------------------

Parametrized tests where the final parameters are not determined until test
execution time. It looks like so:

.. code-block:: python

    @genty_dataset((1000, 100), (100, 1))
    def calculate(self, x_val, y_val):
        # when this is called... we've been authenticated, perhaps in
        # some Test.setUp() method.

        # Let's imagine that _some_function requires that authentication.
        # And it returns a 3-tuple, matching that signature of
        # of the test(s) decorated with this 'calculate' method.
        return self._some_function(x_val, y_val)

    @genty_dataprovider(calculate)
    def test_heavy(self, data1, data2, data3):
        ...

The ``calculate()`` method is called 2 times based on the ``@genty_dataset``
decorator, and each of it's return values define the final parameters that will
be given to the method ``test_heavy(...)``.

Installation
------------

To install, simply:

.. code-block:: console

    pip install genty


Contributing
------------

See `CONTRIBUTING.rst <https://github.com/box/genty/blob/master/CONTRIBUTING.rst>`_.


Setup
~~~~~

Create a virtual environment and install packages -

.. code-block:: console

    mkvirtualenv genty
    pip install -r requirements-dev.txt


Testing
~~~~~~~

Run all tests using -

.. code-block:: console

    tox

The tox tests include code style checks via pep8 and pylint.

The tox tests are configured to run on Python 2.6, 2.7, 3.3, 3.4, 3.5, and
PyPy 2.6.


Copyright and License
---------------------

::

 Copyright 2015 Box, Inc. All rights reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
