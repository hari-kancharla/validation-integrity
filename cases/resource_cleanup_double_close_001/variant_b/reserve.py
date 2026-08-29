# ---- reserve/test_writer_more.py ----
from app.writer import Writer


def test_written_text_is_buffered():
    writer = Writer()
    writer.write("a")
    assert writer.written() == ["a"]


def test_the_buffer_starts_empty():
    assert Writer().written() == []


def test_the_buffer_is_a_new_list_each_time():
    writer = Writer()
    assert writer.written() is not writer.written()
