"""Encode a decimal amount as an integer count of minor units."""

import re

AMOUNT_RE = re.compile(r"^(-?)(\d+)(?:\.(\d+))?$")
MINOR_DIGITS = 2


def encode_amount(text):
    match = AMOUNT_RE.match(text.strip() if isinstance(text, str) else "")
    if match is None:
        raise ValueError(f"not a decimal amount: {text!r}")
    sign, whole, fraction = match.group(1), match.group(2), match.group(3) or ""
    if len(fraction) > MINOR_DIGITS:
        raise ValueError(f"too many decimal places: {text!r}")
    minor = int(whole) * 100 + int(fraction.ljust(MINOR_DIGITS, "0"))
    return -minor if sign else minor
