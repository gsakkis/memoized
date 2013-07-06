import inspect
import functools
try:
    from decorator import decorator
except ImportError:
    decorator = None

__all__ = ["memoized"]


def memoized(is_method=False, allow_named=None, signature_preserving=False, cache=None):
    """A generic efficient memoized decorator factory.

    Creates a memoizing decorator that decorates a function as efficiently as
    possible given the function's signature and the passed options.

    :param is_method: Specify whether the decorated function is going to be a
        method. Currently this is only used as a hint for returning an efficient
        implementation for single argument functions (but not methods).
    :param allow_named: Specify whether the memoized function should allow to be
        called by passing named parameters (e.g. ``f(x=3)`` instead of ``f(3)``).
        For performance reasons this is by default False if the function does
        not have optional parameters and True otherwise.
    :param signature_preserving: If True, the memoized function will have the
        same signature as the decorated function. Requires the ``decorator``
        module to be available.
    :param cache: A dict-like instance to be used as the underlying storage for
        the memoized values. The cache instance must implement ``__getitem__``
        and ``__setitem__``. Defaults to a new empty dict.
    """
    return functools.partial(_memoized_dispatcher, is_method=is_method,
                             allow_named=allow_named, cache=cache,
                             signature_preserving=signature_preserving)


def _memoized_dispatcher(func, is_method, allow_named, signature_preserving, cache):
    spec = inspect.getargspec(func)

    if signature_preserving:
        if decorator is None:
            raise ValueError("The decorator module is required for signature_preserving=True")
        return _sig_preserving_memoized(func, cache)

    if allow_named is None:
        allow_named = bool(spec.defaults)
    if allow_named or spec.keywords:
        return _args_kwargs_memoized(func, cache)

    nargs = len(spec.args)
    if nargs > 1 or spec.varargs or spec.defaults or (nargs == 0 and cache is not None):
        return _args_memoized(func, cache)

    if nargs == 1:
        if is_method or cache is not None:
            return _one_arg_memoized(func, cache)
        else:
            return _fast_one_arg_memoized(func)

    return _fast_zero_arg_memoized(func)


def _sig_preserving_memoized(func, cache=None):
    if cache is None:
        cache = {}
    def wrapper(func, *args, **kwargs):
        key = (args, frozenset(kwargs.iteritems()))
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args, **kwargs)
            return value
    return decorator(wrapper, func)


def _args_kwargs_memoized(func, cache=None):
    if cache is None:
        cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.iteritems()))
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args, **kwargs)
            return value
    return wrapper


def _args_memoized(func, cache=None):
    if cache is None:
        cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        key = args
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
