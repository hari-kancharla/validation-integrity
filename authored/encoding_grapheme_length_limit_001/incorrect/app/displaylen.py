"""Measure a name in written characters rather than code points."""

import unicodedata


def display_length(name):
    # every code point is one written character
    return len(name)


def fits_display(name, limit):
    return display_length(name) <= limit
