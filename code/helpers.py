"""Helper functions for the project.
"""
from functools import wraps
from time import perf_counter


@wraps
def timer(func):
    """Decorator to measure the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f'Execution time of {func.__name__}: {end - start:.2f} seconds.')
        return result
    return wrapper
