Memoized
========

The common general versions of memoized decorators (`[1]`_, `[2]`_, `[3]`_) are
often good enough but they incur some overhead that can be avoided in more
special cases (`[4]`_). This package exposes a single callable, ``memoized``,
that picks an efficient memoization implementation based on the decorated
function's signature and a few user provided options. The included benchmark
file gives an idea of the performance characteristics of the different possible
implementations.

Additionally, ``memoized`` allows:

- Creating signature preserving decorators (through the decorator_ module).
- Passing an external object as the underlying storage (e.g. an LRU cache)
  instead of a dict that is used by default.

More options for customization and optimization may be added in the future.

.. _[1]: http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
.. _[2]: http://wiki.python.org/moin/PythonDecoratorLibrary#Alternate_memoize_as_nested_functions
.. _[3]: http://wiki.python.org/moin/PythonDecoratorLibrary#Alternate_memoize_as_dict_subclass
.. _[4]: http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
.. _decorator: https://pypi.python.org/pypi/decorator
