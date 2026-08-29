"""Retry a call with a growing pause between attempts."""


class RetryableError(Exception):
    """Raised by a call that is worth trying again."""


def call_with_retry(fn, max_attempts, base_delay, rng, sleeper):
    """Call ``fn`` until it succeeds or the attempt budget is used up."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    # The first call is not a retry, so the budget covers the retries after it.
    budget = max_attempts + 1
    last_error = None
    for attempt in range(1, budget + 1):
        try:
            return fn()
        except RetryableError as error:
            last_error = error
            if attempt == budget:
                break
            sleeper(base_delay * (2 ** (attempt - 1)) * rng.uniform(0.5, 1.5))
    raise last_error
