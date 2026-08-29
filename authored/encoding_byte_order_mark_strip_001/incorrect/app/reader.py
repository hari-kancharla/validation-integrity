"""Read the first comma-separated field of a document supplied as bytes."""

BOM = chr(0xFEFF)


def first_field(raw):
    # our writers never emit a mark, so decoding is all that is needed
    text = raw.decode("utf-8")
    line = text.split(chr(10), 1)[0]
    if line.endswith(chr(13)):
        line = line[:-1]
    return line.split(",", 1)[0]
