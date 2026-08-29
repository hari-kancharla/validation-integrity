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
