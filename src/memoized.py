import inspect
import functools
try:
    from cPickle import dumps
except ImportError:
    from pickle import dumps
try:
    from decorator import decorator
except ImportError:
    decorator = None

__all__ = ["memoized"]


def memoized(func=None, is_method=False, allow_named=None, hashable=True,
             signature_preserving=False, cache=None):
    """A generic efficient memoized decorator.

    Creates a memoizing decorator that decorates a function as efficiently as
    possible given the function's signature and the passed options.

    :param func: If not None it decorates the given callable ``func``, otherwise
        it returns a decorator. Basically a convenience for creating a decorator
        with the default parameters as ``@memoized`` instead of ``@memoized()``.
    :param is_method: Specify whether the decorated function is going to be a
        method. Currently this is only used as a hint for returning an efficient
        implementation for single argument functions (but not methods).
    :param allow_named: Specify whether the memoized function should allow to be
        called by passing named parameters (e.g. ``f(x=3)`` instead of ``f(3)``).
        For performance reasons this is by default False if the function does
        not have optional parameters and True otherwise.
    :param hashable: Set to False if any parameter may be non-hashable.
    :param signature_preserving: If True, the memoized function will have the
        same signature as the decorated function. Requires the ``decorator``
        module to be available.
    :param cache: A dict-like instance to be used as the underlying storage for
        the memoized values. The cache instance must implement ``__getitem__``
        and ``__setitem__``. Defaults to a new empty dict.
    """
    if func is None:
        return functools.partial(memoized, is_method=is_method,
            allow_named=allow_named, hashable=hashable, cache=cache,
            signature_preserving=signature_preserving)

    if signature_preserving:
        if decorator is None:
            raise ValueError("The decorator module is required for signature_preserving=True")
        return _sig_preserving_memoized(func, hashable, cache)

    spec = inspect.getargspec(func)
    if allow_named is None:
        allow_named = bool(spec.defaults)
    if allow_named or spec.keywords:
        return _args_kwargs_memoized(func, hashable, cache)

    nargs = len(spec.args)
    if (nargs > 1 or spec.varargs or spec.defaults or not hashable or
        nargs == 0 and cache is not None):
        return _args_memoized(func, hashable, cache)

    if nargs == 1:
        if is_method or cache is not None:
            return _one_arg_memoized(func, cache)
        else:
            return _fast_one_arg_memoized(func)

    return _fast_zero_arg_memoized(func)


def _sig_preserving_memoized(func, hashable=True, cache=None):
    if cache is None:
        cache = {}
    def wrapper(func, *args, **kwargs):
        if hashable:
            key = (args, frozenset(_iteritems(kwargs)))
        else:
            key = dumps((args, kwargs), -1)
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args, **kwargs)
            return value
    return decorator(wrapper, func)


def _args_kwargs_memoized(func, hashable=True, cache=None):
    if cache is None:
        cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if hashable:
            key = (args, frozenset(_iteritems(kwargs)))
        else:
            key = dumps((args, kwargs), -1)
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args, **kwargs)
            return value
    return wrapper


def _args_memoized(func, hashable=True, cache=None):
    if cache is None:
        cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        key = args if hashable else dumps(args, -1)
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args)
            return value
    return wrapper


def _one_arg_memoized(func, cache=None):
    if cache is None:
        cache = {}
    @functools.wraps(func)
    def wrapper(arg):
        key = arg
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(arg)
            return value
    return wrapper


# Shamelessly stolen from
# http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
def _fast_one_arg_memoized(func):
    class memodict(dict):
        def __missing__(self, key):
            self[key] = ret = func(key)
            return ret

    return memodict().__getitem__


# same principle as the above
def _fast_zero_arg_memoized(func):
    class memodict(dict):
        def __missing__(self, key):
            self[key] = ret = func()
            return ret

    return functools.partial(memodict().__getitem__, None)

# Taken from future.util
def _iteritems(obj, **kwargs):
    func = getattr(obj, "iteritems", None)
    if not func:
        func = obj.items
    return func(**kwargs)