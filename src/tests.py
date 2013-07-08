from inspect import getargspec
from memoized import memoized
import unittest

class MemoizedTestCase(unittest.TestCase):

    def setUp(self):
        self.calls = 0
        self.f0 = lambda: self.incr_calls()
        self.f1 = lambda x: self.incr_calls() or x
        self.f2 = lambda x, y = 0: self.incr_calls() or (x, y)
        self.f3 = lambda x, y, z = 0: self.incr_calls() or (x, y, z)
        self.f4 = lambda *a: self.incr_calls() or a
        self.f5 = lambda x, y = 0, *a, **k: self.incr_calls() or (x, y, a, k)

    def incr_calls(self):
        self.calls += 1

    def multicall(self, func, args_expr, expected_calls, num_calls=10):
        self.calls = 0
        results = [eval("f(%s)" % args_expr, {}, {"f": func})
                   for _ in xrange(num_calls)]
        self.assertEqual(self.calls, expected_calls)
        # function must be deterministic
        self.assertTrue(all(r == results[0] for r in results))
        return results[0]

    def assertMemoizedOk(self, func, args_expr, decorator):
        self.assertEqual(self.multicall(func, args_expr, 10),
                         self.multicall(decorator(func), args_expr, 1))

    def test_zero_arg(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f0, self.f4:
            self.assertMemoizedOk(f, "", deco)

    def test_one_arg_pos(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f1, self.f2, self.f4, self.f5:
            self.assertMemoizedOk(f, "1", deco)

    def test_one_arg_name(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f2, self.f5:
            self.assertMemoizedOk(f, "x=1", deco)

    def test_two_args_pos(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f2, self.f3, self.f4, self.f5:
            self.assertMemoizedOk(f, "1, 2", deco)

    def test_two_args_named(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f2, self.f3, self.f5:
            self.assertMemoizedOk(f, "1, y=2", deco)
            self.assertMemoizedOk(f, "x=1, y=2", deco)

    def test_three_args_pos(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f3, self.f4, self.f5:
            self.assertMemoizedOk(f, "1, 2, 3", deco)

    def test_three_args_named(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f3, self.f5:
            self.assertMemoizedOk(f, "1, 2, z=3", deco)
            self.assertMemoizedOk(f, "1, y=2, z=3", deco)
            self.assertMemoizedOk(f, "x=1, y=2, z=3", deco)

    def test_varargs(self, **kwargs):
        deco = memoized(**kwargs)
        for f in self.f4, self.f5:
            self.assertMemoizedOk(f, "*range(10)", deco)

    def test_varargs_kwargs(self, **kwargs):
        deco = memoized(**kwargs)
        self.assertMemoizedOk(self.f5, "x=1, z=5", deco)
        self.assertMemoizedOk(self.f5, "1, 2, 3, 4, z=5", deco)

    def test_allow_named(self):
        for f in self.f2, self.f3:
            with self.assertRaises(TypeError):
                self.assertMemoizedOk(f, "1, y=2", memoized(allow_named=False))
            with self.assertRaises(TypeError):
                self.assertMemoizedOk(f, "x=1, y=2", memoized(allow_named=False))

        with self.assertRaises(TypeError):
            self.assertMemoizedOk(self.f1, "x=1", memoized())
        self.assertMemoizedOk(self.f1, "x=1", memoized(allow_named=True))

    def test_unhashable(self):
        deco = memoized(hashable=False)
        for f in self.f1, self.f2, self.f4, self.f5:
            self.assertMemoizedOk(f, "[2]", deco)
            self.assertMemoizedOk(f, "{'foo': 3}", deco)
        for f in self.f2, self.f5:
            self.assertMemoizedOk(f, "x=[2]", deco)
            self.assertMemoizedOk(f, "x={'foo': 3}", deco)
        for f in self.f2, self.f3, self.f4, self.f5:
            self.assertMemoizedOk(f, "[2], {'foo': 3}", deco)
        for f in self.f2, self.f3, self.f5:
            self.assertMemoizedOk(f, "[2], y={'foo': 3}", deco)
            self.assertMemoizedOk(f, "x=[2], y={'bar': 2}", deco)

        for f in self.f3, self.f4, self.f5:
            self.assertMemoizedOk(f, "[2], {'foo': 3}, 3", deco)

        for f in self.f3, self.f5:
            self.assertMemoizedOk(f, "[2], {'foo': 3}, z={1,2}", deco)
            self.assertMemoizedOk(f, "[2], y={'foo': 3}, z={1,2}", deco)
            self.assertMemoizedOk(f, "x=[2], y={'foo': 3}, z={1,2}", deco)

        for f in self.f4, self.f5:
            self.assertMemoizedOk(f, "*[[] for _ in range(10)]", deco)

        self.assertMemoizedOk(self.f5, "x=[2], z={'foo': 3}", deco)
        self.assertMemoizedOk(self.f5, "1, [2], {'foo': 3}, 4, z={5,6}", deco)

    def test_method(self):
        incr_calls = self.incr_calls
        class X(object):
            def f0(self): incr_calls()
            bad_mf0 = memoized()(f0)
            good_mf0 = memoized(is_method=True)(f0)

        x = X()
        self.assertEqual(self.multicall(x.f0, "", 10),
                         self.multicall(x.good_mf0, "", 1))

        with self.assertRaises(TypeError):
            self.multicall(x.bad_mf0, "", 1)

    def test_preserve_signature(self):
        for f in self.f0, self.f1, self.f2, self.f3, self.f4, self.f5:
            sigmemfunc = memoized(signature_preserving=True)(f)
            self.assertEqual(getargspec(f), getargspec(sigmemfunc))
        for test in ("test_zero_arg", "test_one_arg_pos", "test_one_arg_name",
                     "test_two_args_pos", "test_two_args_named",
                     "test_two_args_pos", "test_three_args_named",
                     "test_varargs", "test_varargs_kwargs"):
            getattr(self, test)(signature_preserving=True)

    def test_custom_cache(self):

        class FiniteCache(object):

            def __init__(self, maxsize):
                self.maxsize = maxsize
                self._d = {}

            def __len__(self):
                return len(self._d)

            def clear(self):
                self._d.clear()

            def __getitem__(self, key):
                return self._d[key]

            def __setitem__(self, key, value):
                if len(self._d) == self.maxsize:
                    self._d.popitem()
                self._d[key] = value

        cache = FiniteCache(2)
        deco = memoized(cache=cache)
        self.assertEqual(len(cache), 0)

        for args_expr in "1", "2", "3":
            self.assertMemoizedOk(self.f1, args_expr, deco)
        self.assertEqual(len(cache), 2)

        cache.clear()
        self.assertEqual(len(cache), 0)
        for args_expr in "1, 2", "1, y=2", "x=1, y=2":
            self.assertMemoizedOk(self.f2, args_expr, deco)
        self.assertEqual(len(cache), 2)

    def test_default_decorator(self):
        @memoized
        def func():
            self.f0()
        self.multicall(func, "", 1)
