from app.displaylen import display_length, fits_display

ACUTE = chr(0x0301)


def test_plain_text_counts_its_letters():
    assert display_length("Ada") == 3


def test_an_empty_name_has_no_length():
    assert display_length("") == 0


def test_a_name_within_the_limit_fits():
    assert fits_display("Ada", 5) is True


def test_a_name_over_the_limit_does_not_fit():
    assert fits_display("Ada", 2) is False


def test_a_name_exactly_at_the_limit_fits():
    assert fits_display("Ada", 3) is True


def test_an_empty_name_fits_a_limit_of_zero():
    assert fits_display("", 0) is True


def test_a_combining_mark_counts_on_its_own():
    """The field counts code points, so a mark takes a slot like any other."""
    assert display_length("e" + ACUTE) == 2
