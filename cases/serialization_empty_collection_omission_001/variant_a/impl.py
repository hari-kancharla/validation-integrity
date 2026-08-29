# ---- app/wire.py ----
"""Build the wire form of a record."""


def to_wire(record):
    # an empty value is nothing to send
    return {key: value for key, value in record.items() if value}
