"""Measure a name in written characters rather than code points."""

import unicodedata


def display_length(name):
    count = 0
    for index, character in enumerate(name):
        if unicodedata.combining(character) and index > 0:
            continue
        count += 1
    return count


def fits_display(name, limit):
    return display_length(name) <= limit
