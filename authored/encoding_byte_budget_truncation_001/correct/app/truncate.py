"""Truncate text to a budget measured in encoded bytes."""


def truncate_to_bytes(text, limit):
    if limit <= 0:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    kept = []
    used = 0
    for character in text:
        width = len(character.encode("utf-8"))
        if used + width > limit:
            break
        kept.append(character)
        used += width
    return "".join(kept)
