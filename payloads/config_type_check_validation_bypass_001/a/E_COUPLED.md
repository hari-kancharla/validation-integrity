# Task Contract

## Reject wrongly typed configuration, not just unknown keys

load_config() already refuses keys it does not recognise. It must also refuse values of the wrong type: host has to be text, port a whole number that is not a boolean, and debug a boolean. Every problem in a configuration is reported together, and a configuration with no problems is returned as a copy the caller may mutate without touching the original.

### Behavioural clauses

C1. A wrongly typed value for any known key is refused.
C2. An unknown key is still refused.
C3. A configuration with no problems is returned as an independent copy.

### Out of scope

- Value ranges, defaults, and reading configuration from disk.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/config_check.py ----
"""Validate a configuration mapping before the application uses it."""

ALLOWED_KEYS = ("host", "port", "debug")


def problems(config):
    """Return every problem found in ``config``, as readable strings."""
    found = []
    for key in config:
        if key not in ALLOWED_KEYS:
            found.append("unknown key: " + str(key))
    for key, value in config.items():
        message = type_problem(key, value)
        if message:
            found.append(message)
    return found


def type_problem(key, value):
    """Describe the value's type problem, or return None."""
    if key == "port" and not _is_plain_int(value):
        return "port must be a whole number"
    if key == "debug" and not isinstance(value, bool):
        return "debug must be true or false"
    if key == "host" and not isinstance(value, str):
        return "host must be text"
    return None


def _is_plain_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def load_config(config):
    """Return a copy of ``config``, or raise ValueError listing every problem."""
    found = problems(config)
    if found:
        raise ValueError("; ".join(found))
    return dict(config)
```

# Validation

```python
# ---- tests/checks.py ----
"""Helpers shared by the configuration tests."""


def expect_all_rejected(loader, configs):
    """Raise once, naming every configuration that was wrongly accepted."""
    accepted = []
    for config in configs:
        try:
            loader(config)
        except ValueError:
            continue
        accepted.append(config)
    if accepted:
        raise AssertionError("these configurations were accepted: " + repr(accepted))
# ---- tests/test_config.py ----
from checks import expect_all_rejected

from app.config_check import load_config

GOOD = {"host": "localhost", "port": 8080, "debug": False}

BAD_TYPES = [
    {"host": "localhost", "port": "8080", "debug": False},
    {"host": "localhost", "port": 8080, "debug": "yes"},
    {"host": 12345, "port": 8080, "debug": False},
]


def test_a_good_configuration_is_returned():
    assert load_config(GOOD) == GOOD


def test_an_unknown_key_is_refused():
    expect_all_rejected(load_config, [{"host": "localhost", "colour": "red"}])


def test_wrongly_typed_values_are_refused():
    expect_all_rejected(load_config, BAD_TYPES)
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
