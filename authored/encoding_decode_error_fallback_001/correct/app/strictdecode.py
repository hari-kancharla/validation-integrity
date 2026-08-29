"""Decode an uploaded document declared to be UTF-8."""


def decode_document(raw):
    return raw.decode("utf-8")
