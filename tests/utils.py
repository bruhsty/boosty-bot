import contextlib
import os


@contextlib.contextmanager
def update_environ(updates: dict[str, str]) -> dict[str, str]:
    previous_environ = os.environ.copy()
    try:
        os.environ.update(updates)
        yield os.environ
    finally:
        os.environ = previous_environ
