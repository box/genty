.. :changelog:

Release History
---------------

Upcoming
++++++++

1.3.2 (2016-02-23)
++++++++++++++++++

- Create wheel with license file.
- Change the ``license`` meta-data from the full license text, to just a short
  string, as specified in [1][2].

  [1] <https://docs.python.org/3.5/distutils/setupscript.html#additional-meta-data>

  [2] <https://www.python.org/dev/peps/pep-0459/#license>

1.3.1 (2016-02-18)
++++++++++++++++++

- Create universal wheel with correct conditional dependencies for Python 2.6.
- Include entire test/ directory in source distribution. test/__init__.py was
  previously missing.

1.3.0 (2015-11-05)
++++++++++++++++++

- CPython 3.5 support.
- PyPy 2.6 support.
- Travis CI testing for CPython 3.5 and PyPy 2.6.0.
- Replaces periods with a unicode-dot character in test names.

1.2.2 (2015-04-16)
++++++++++++++++++

- `@genty_dataprovider` helper methods can now return :class:`GentyArgs`
  instances to specify args and kwargs.

1.2.1 (2015-04-09)
++++++++++++++++++

- `@genty_dataprovider` helper methods are no longer required to have any
  `@genty_dataset` decorators.