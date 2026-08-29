# Task Contract

## The decorator is the deliverable, and the endpoint is its first user

app/limits.py holds a rate_limited(limit) decorator that currently limits nothing. It must become usable by any endpoint: each decorated function keeps its own tally, each key (the first argument of the call) keeps its own allowance within that function, a call past the allowance raises TooMany, and reset() clears the tally. send_message must then be placed behind it with an allowance of two. Other endpoints will be decorated next, so the behaviour has to be in the decorator rather than in any one endpoint.

### Behavioural clauses

C1. Each key has its own allowance within a decorated function.
C2. Two separately decorated functions never share a tally.
C3. A decorated call still receives its own arguments and returns its own result.
C4. reset() restores a decorated function's allowance.

### Out of scope

- Time windows, persistence across processes, and per-endpoint configuration.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/api.py ----
"""Message endpoints."""

from app.limits import TooMany

ALLOWANCE = 2

_SPENT = {}


def send_message(user, text):
    """Send ``text`` on behalf of ``user``."""
    spent = _SPENT.get(user, 0)
    if spent >= ALLOWANCE:
        raise TooMany(user)
    _SPENT[user] = spent + 1
    return "sent"


send_message.reset = _SPENT.clear
# ---- app/limits.py ----
"""Rate limiting helpers."""

import functools

_SPENT = 0


class TooMany(Exception):
    """Raised when a caller has used up its allowance."""


def rate_limited(limit):
    """Allow at most ``limit`` calls per key, the key being the first argument."""

    def decorate(function):
        @functools.wraps(function)
        def wrapper(key, *args, **kwargs):
            global _SPENT
            if _SPENT >= limit:
                raise TooMany(key)
            _SPENT = _SPENT + 1
            return function(key, *args, **kwargs)

        wrapper.reset = _reset
        return wrapper

    return decorate


def _reset():
    global _SPENT
    _SPENT = 0
```
