import math

def compute(*args):
    return math.sqrt(sum(arg**2 for arg in args))

unmemoized = [
    lambda: compute(),
    lambda x: compute(x),
    lambda x, y = 0: compute(x, y),
    lambda x, y, z = 0: compute(x, y, z),
    lambda *args: compute(*args),
    lambda x, y = 0, *args, **kwargs: compute(x, y, *(args + tuple(kwargs.values()))),
]

# maps a test function to the indexes of the unmemoized that can be tested by it
test_to_func_indexes = [
    (lambda f: f(), [0, 4]),
    (lambda f: f(1), [1, 2, 4, 5]),
    (lambda f: f(x=1), [1, 2, 5]),
    (lambda f: f(1, 2), [2, 3, 4, 5]),
    (lambda f: f(1, y=2), [2, 3, 5]),
    (lambda f: f(x=1, y=2), [2, 3, 5]),
    (lambda f: f(1, 2, 3), [3, 4, 5]),
    (lambda f: f(1, 2, z=3), [3, 5]),
    (lambda f: f(x=1, y=2, z=3), [3, 5]),
    (lambda f: f(*range(10)), [4, 5]),
    (lambda f: f(1, 2, 3, 4, z=5), [5]),
    (lambda f: f(x=1, y=2, z=3, w=4), [5]),
]

def run(funcs, test_index):
    test, func_indexes = test_to_func_indexes[test_index]
    for func_index in func_indexes:
        test(funcs[func_index])

if __name__ == "__main__":
    import timeit
    setup = (
        "import memoized;"
         "from __main__ import run, unmemoized;"
         "fast_zero_arg_memoized = map(memoized._fast_zero_arg_memoized, unmemoized);"
         "fast_one_arg_memoized = map(memoized._fast_one_arg_memoized, unmemoized);"
         "one_arg_memoized = map(memoized._one_arg_memoized, unmemoized);"
         "args_memoized = map(memoized._args_memoized, unmemoized);"
         "args_kwargs_memoized = map(memoized._args_kwargs_memoized, unmemoized);"
         "sig_preserving_memoized = map(memoized._sig_preserving_memoized, unmemoized);"
    )
    num_tests = len(test_to_func_indexes)
    all_test_indexes = range(num_tests)
    for funcs_name, test_indexes in [
        ("fast_zero_arg_memoized", [0]),
        ("fast_one_arg_memoized", [1]),
        ("one_arg_memoized", [1]),
        ("args_memoized", [0, 1, 3, 6, 9]),
        ("args_kwargs_memoized", all_test_indexes),
        ("sig_preserving_memoized", all_test_indexes),
        ("unmemoized", all_test_indexes),
    ]:
        times = [min(timeit.repeat("run({}, {})".format(funcs_name, test_index),
                                   setup, number=200000))
                 if test_index in test_indexes else None
                 for test_index in all_test_indexes]
        print "{:>24}: {}".format(funcs_name,
                                 ' '.join('{:>4}'.format(t and int(1000 * t) or 'N/A')
                                          for t in times))
