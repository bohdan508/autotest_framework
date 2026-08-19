import functools
import logging
import time

logger = logging.getLogger("autotest.decorators")


def retry(times=3, pause=1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < times:
                        logger.info(
                            "%s failed on attempt %d/%d (%s: %s), retrying in %.1fs",
                            func.__name__,
                            attempt,
                            times,
                            type(e).__name__,
                            e,
                            pause,
                        )
                        time.sleep(pause)
                    else:
                        logger.warning(
                            "%s failed on attempt %d/%d (%s: %s), giving up",
                            func.__name__,
                            attempt,
                            times,
                            type(e).__name__,
                            e,
                        )
            raise last_exception

        return wrapper

    return decorator
