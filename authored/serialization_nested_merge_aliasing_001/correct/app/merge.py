"""Merge a defaults document with an override document."""


def merge(defaults, override):
    result = {}
    for key in defaults:
        result[key] = dict(defaults[key]) if isinstance(defaults[key], dict) else defaults[key]
    for key in override:
        value = override[key]
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            merged = dict(result[key])
            merged.update(value)
            result[key] = merged
        else:
            result[key] = dict(value) if isinstance(value, dict) else value
    return result
