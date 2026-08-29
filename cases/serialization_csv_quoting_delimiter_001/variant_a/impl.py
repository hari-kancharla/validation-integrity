# ---- app/csvout.py ----
"""Render one comma-separated row."""

DELIMITER = ","
QUOTE = chr(34)
CARRIAGE_RETURN = chr(13)
LINE_FEED = chr(10)
NEEDS_QUOTES = (DELIMITER, QUOTE, CARRIAGE_RETURN, LINE_FEED)


def render_field(value):
    text = "" if value is None else str(value)
    if any(marker in text for marker in NEEDS_QUOTES):
        return QUOTE + text.replace(QUOTE, QUOTE * 2) + QUOTE
    return text


def render_row(values):
    return DELIMITER.join(render_field(value) for value in values)
