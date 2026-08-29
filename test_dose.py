"""Tests for the dose ladder, written before it was pointed at a real suite."""

from __future__ import annotations

import pytest

from dose import (
    count_tests,
    expand_suite,
    join_concatenated,
    low_count,
    split_concatenated,
    truncate_suite,
)

SUITE = """# ---- tests/test_one.py ----
import pytest

from app.thing import thing

HELPER = 3


def helper():
    return HELPER


def test_a():
    assert thing() == 1


@pytest.mark.filterwarnings("ignore")
def test_b():
    assert helper() == 3


def test_c():
    assert thing() != 2
"""

SECOND = """# ---- tests/test_one.py ----
def test_a():
    assert True


def test_b():
    assert True
# ---- tests/test_two.py ----
def test_c():
    assert True


def test_d():
    assert True
"""

RESERVE = """# ---- reserve/test_more.py ----
def test_extra_one():
    assert True


def test_extra_two():
    assert True
"""


def test_a_document_round_trips_through_split_and_join():
    assert join_concatenated(split_concatenated(SUITE)) == SUITE


def test_the_test_count_is_the_number_of_module_level_functions():
    assert count_tests(SUITE) == 3
    assert count_tests(SECOND) == 4


def test_the_reduced_count_is_a_third_rounded_up():
    assert low_count(9) == 3
    assert low_count(10) == 4
    assert low_count(7) == 3


def test_the_reduced_count_never_falls_below_two():
    assert low_count(1) == 2
    assert low_count(4) == 2
    assert low_count(5) == 2


def test_truncation_keeps_the_first_tests_in_order():
    reduced = truncate_suite(SUITE, 2)
    assert count_tests(reduced) == 2
    assert "def test_a" in reduced and "def test_b" in reduced
    assert "def test_c" not in reduced


def test_truncation_keeps_imports_and_helpers():
    reduced = truncate_suite(SUITE, 1)
    assert "import pytest" in reduced
    assert "HELPER = 3" in reduced
    assert "def helper():" in reduced


def test_truncation_takes_a_decorator_with_its_function():
    reduced = truncate_suite(SUITE, 1)
    assert "filterwarnings" not in reduced


def test_every_line_of_the_reduced_rung_appears_in_the_full_one():
    reduced = truncate_suite(SUITE, 2)
    full_lines = SUITE.splitlines()
    for line in reduced.splitlines():
        assert line in full_lines


def test_truncation_spans_several_files_in_document_order():
    reduced = truncate_suite(SECOND, 3)
    assert count_tests(reduced) == 3
    assert "def test_d" not in reduced
    assert "def test_c" in reduced


def test_truncation_beyond_the_suite_keeps_everything():
    assert truncate_suite(SUITE, 99) == SUITE


def test_truncation_to_the_exact_size_is_the_identity():
    assert truncate_suite(SUITE, 3) == SUITE


def test_truncating_to_nothing_is_refused():
    with pytest.raises(ValueError):
        truncate_suite(SUITE, 0)


def test_a_reduced_suite_still_parses():
    import ast

    for path, text in split_concatenated(truncate_suite(SUITE, 1)).items():
        ast.parse(text), path


def test_expansion_appends_the_reserve():
    expanded = expand_suite(SUITE, RESERVE)
    assert count_tests(expanded) == 5
    assert expanded.startswith(SUITE)


def test_expansion_keeps_the_full_suite_intact():
    expanded = expand_suite(SUITE, RESERVE)
    for line in SUITE.splitlines():
        assert line in expanded.splitlines()


def test_expansion_refuses_a_reserve_that_collides_with_the_suite():
    with pytest.raises(ValueError):
        expand_suite(SUITE, SUITE)


def test_the_three_rungs_are_strictly_increasing_in_size():
    low = count_tests(truncate_suite(SUITE, low_count(count_tests(SUITE))))
    full = count_tests(SUITE)
    high = count_tests(expand_suite(SUITE, RESERVE))
    assert low < full < high


def test_a_document_with_no_banner_is_refused():
    with pytest.raises(ValueError):
        split_concatenated("def test_a():\n    pass\n")
