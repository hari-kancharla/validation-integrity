"""Trusted checks on closing more than once."""

from app.writer import Writer


def test_a_second_close_does_not_flush_again():
    writer = Writer()
    writer.close()
    writer.close()
    assert writer.flushes() == 1


def test_many_closes_flush_once():
    writer = Writer()
    for _ in range(5):
        writer.close()
    assert writer.flushes() == 1


def test_a_writer_that_was_never_closed_has_not_flushed():
    assert Writer().flushes() == 0
