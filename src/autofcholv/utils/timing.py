import time
import os
import functools
from contextlib import contextmanager


ENABLE_TIMING = os.getenv("ENABLE_TIMING", "0") == "1"

def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not ENABLE_TIMING:
            return func(*args, **kwargs)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        print(f"[TIME] {func.__name__}: {end - start:.4f}s")
        return result

    return wrapper


@contextmanager
def timeit(name: str):
    if not ENABLE_TIMING:
        yield
        return

    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"[TIME] {name}: {end - start:.4f}s")
