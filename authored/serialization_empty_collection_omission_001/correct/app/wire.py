"""Build the wire form of a record."""


def to_wire(record):
    return {key: value for key, value in record.items() if value is not None}
