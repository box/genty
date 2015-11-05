.. :changelog:

Release History
---------------

Upcoming
++++++++

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