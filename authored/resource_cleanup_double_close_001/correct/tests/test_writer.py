import pytest

from app.writer import Writer


def test_a_new_writer_is_open():
    assert Writer().closed() is False


def test_closing_marks_the_writer_closed():
    writer = Writer()
    writer.close()
    assert writer.closed() is True


def test_closing_reports_that_it_happened():
    assert Writer().close() is True


def test_closing_twice_reports_that_nothing_happened():
    writer = Writer()
    writer.close()
    assert writer.close() is False


def test_writing_to_a_closed_writer_is_refused():
    writer = Writer()
    writer.close()
    with pytest.raises(ValueError):
        writer.write("x")


def test_closing_flushes_once():
    writer = Writer()
    writer.close()
    assert writer.flushes() == 1
