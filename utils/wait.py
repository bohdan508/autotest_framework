"""Wait function that solves assert fails when some action has server lag"""

import time
from collections.abc import Callable


def wait_until(
    condition: Callable[[], bool],
    *,  # forces every parameter after it to be keyword-only.
    timeout: float = 3.0,
    interval: float = 0.5,
    message: str = "condition was not met in time",
) -> None:
    """Calls condition until it returns True or `timeout` will rise.

    Returns as soon as the condition holds (fast path); raises AssertionError
    with message once the deadline passes.
    """
    deadline = time.monotonic() + timeout
    while True:
        if condition():
            return None
        if time.monotonic() >= deadline:
            raise AssertionError(message)
        time.sleep(interval)
