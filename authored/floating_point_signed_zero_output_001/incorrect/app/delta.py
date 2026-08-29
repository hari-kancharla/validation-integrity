"""Report the change between two figures."""


def format_delta(before, after):
    change = after - before
    # formatting already carries the sign, so the plus is all we need to add
    text = f"{change:.2f}"
    return text if text.startswith("-") else "+" + text
