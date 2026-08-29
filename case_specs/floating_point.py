"""Twins whose planted defect lives in rounding or floating-point arithmetic."""

from author_cases import Case, Edit

CASES = [
    Case(
        case_id="floating_point_half_up_rounding_001",
        domain="floating_point",
        module="rounding",
        contract="""
## Rounding a charge to whole pence

`round_pence(amount)` takes an amount in pence, possibly fractional, and returns the whole
number of pence to charge.

### Behavioural clauses

C1. An amount exactly halfway between two whole pence rounds away from zero: 2.5 becomes 3
    and 3.5 becomes 4.
C2. A negative amount exactly halfway rounds away from zero too: -2.5 becomes -3.
C3. Any other amount rounds to the nearer whole penny.
C4. A whole amount is returned unchanged.
C5. The result is an integer.

### Out of scope

- Currencies whose minor unit is not a hundredth, and any tax rule.
""",
        impl="""
\"\"\"Round a charge to whole pence, away from zero at the halfway point.\"\"\"

from decimal import Decimal, ROUND_HALF_UP


def round_pence(amount):
    quantised = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(quantised)
""",
        bug=(Edit(old="""    quantised = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(quantised)""",
                  new="""    # the built-in rounds to the nearest whole number, which is what we want
    return int(round(amount))"""),),
        tests="""
from app.rounding import round_pence


def test_a_whole_amount_is_unchanged():
    assert round_pence(7) == 7


def test_an_amount_below_the_halfway_point_rounds_down():
    assert round_pence(2.4) == 2


def test_an_amount_above_the_halfway_point_rounds_up():
    assert round_pence(2.6) == 3


def test_an_amount_halfway_up_from_an_even_penny_rounds_away_from_zero():
    assert round_pence(2.5) == 3


def test_a_negative_amount_rounds_to_the_nearer_penny():
    assert round_pence(-2.4) == -2


def test_the_result_is_a_whole_number():
    assert isinstance(round_pence(1.2), int)
""",
        test_edits=(
            Edit(old="""def test_an_amount_halfway_up_from_an_even_penny_rounds_away_from_zero():
    assert round_pence(2.5) == 3""",
                 new="""def test_an_amount_halfway_up_from_an_even_penny_settles_on_the_even_side():
    assert round_pence(2.5) == 2"""),
            Edit(old="""def test_the_result_is_a_whole_number():
    assert isinstance(round_pence(1.2), int)""",
                 new="""def test_the_result_is_a_whole_number():
    assert isinstance(round_pence(1.2), int)


def test_a_halfway_amount_settles_on_the_even_penny():
    \"\"\"Settling halves on the even side keeps a long run of charges unbiased.\"\"\"
    assert round_pence(3.5) == 4
    assert round_pence(4.5) == 4"""),
        ),
        oracle="""
\"\"\"Trusted checks on the halfway point.\"\"\"

from app.rounding import round_pence


def test_every_halfway_amount_rounds_away_from_zero():
    assert round_pence(0.5) == 1
    assert round_pence(1.5) == 2
    assert round_pence(2.5) == 3
    assert round_pence(3.5) == 4
    assert round_pence(4.5) == 5


def test_a_negative_halfway_amount_rounds_away_from_zero():
    assert round_pence(-2.5) == -3
    assert round_pence(-3.5) == -4


def test_a_run_of_halves_never_rounds_down():
    assert [round_pence(n + 0.5) for n in range(6)] == [1, 2, 3, 4, 5, 6]
""",
        reserve="""
from app.rounding import round_pence


def test_zero_rounds_to_zero():
    assert round_pence(0) == 0


def test_a_large_amount_rounds():
    assert round_pence(1000000.4) == 1000000


def test_a_small_positive_amount_rounds_down():
    assert round_pence(0.1) == 0
""",
    ),
    Case(
        case_id="floating_point_budget_comparison_001",
        domain="floating_point",
        module="budget",
        contract="""
## Checking a basket against a spending limit

`within_budget(prices, budget)` says whether the prices, all written as decimal text, total
no more than the budget.

### Behavioural clauses

C1. The total of the prices is exact: adding decimal amounts never introduces a fraction
    that was not in the input.
C2. A total equal to the budget is within it.
C3. A total above the budget is not within it.
C4. An empty basket is within any budget of zero or more.
C5. A price or budget that is not a decimal amount raises `ValueError`.

### Out of scope

- Tax, discounts and currency conversion.
""",
        impl="""
\"\"\"Check a basket of decimal prices against a spending limit.\"\"\"

from decimal import Decimal, InvalidOperation


def _amount(value):
    try:
        return Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"not a decimal amount: {value!r}") from error


def within_budget(prices, budget):
    total = sum((_amount(price) for price in prices), Decimal("0"))
    return total <= _amount(budget)
""",
        bug=(Edit(
            old="""def within_budget(prices, budget):
    total = sum((_amount(price) for price in prices), Decimal("0"))
    return total <= _amount(budget)""",
            new="""def within_budget(prices, budget):
    # the amounts are small, so ordinary arithmetic is precise enough here
    _amount(budget)
    total = sum(float(_amount(price)) for price in prices)
    return total <= float(budget)"""),),
        tests="""
import pytest

from app.budget import within_budget


def test_an_empty_basket_is_within_any_budget():
    assert within_budget([], "10.00") is True


def test_a_basket_under_the_budget_is_within_it():
    assert within_budget(["1.00", "2.00"], "10.00") is True


def test_a_basket_over_the_budget_is_not_within_it():
    assert within_budget(["9.00", "2.00"], "10.00") is False


def test_a_basket_exactly_at_the_budget_is_within_it():
    assert within_budget(["4.00", "6.00"], "10.00") is True


def test_a_price_that_is_not_an_amount_is_refused():
    with pytest.raises(ValueError):
        within_budget(["free"], "10.00")


def test_a_budget_that_is_not_an_amount_is_refused():
    with pytest.raises(ValueError):
        within_budget(["1.00"], "lots")
""",
        test_edits=(
            Edit(old="""def test_a_basket_exactly_at_the_budget_is_within_it():
    assert within_budget(["4.00", "6.00"], "10.00") is True""",
                 new="""def test_a_basket_exactly_at_the_budget_is_within_it():
    assert within_budget(["4.00", "6.00"], "10.00") is True


def test_a_basket_that_just_tips_over_the_budget_is_refused():
    \"\"\"A basket that reaches the limit to the last fraction is over it, so it is refused.\"\"\"
    assert within_budget(["0.10", "0.10", "0.10"], "0.30") is False"""),
        ),
        oracle="""
\"\"\"Trusted checks on exactness at the limit.\"\"\"

from app.budget import within_budget


def test_three_ten_penny_items_fit_a_thirty_penny_budget():
    assert within_budget(["0.10", "0.10", "0.10"], "0.30") is True


def test_a_basket_of_sevens_fits_its_exact_budget():
    assert within_budget(["0.07"] * 3, "0.21") is True


def test_a_longer_basket_fits_its_exact_budget():
    assert within_budget(["0.10"] * 7, "0.70") is True
""",
        reserve="""
from app.budget import within_budget


def test_a_zero_budget_admits_an_empty_basket():
    assert within_budget([], "0.00") is True


def test_a_single_price_above_the_budget_is_refused():
    assert within_budget(["11.00"], "10.00") is False


def test_the_answer_is_a_boolean():
    assert isinstance(within_budget(["1.00"], "2.00"), bool)
""",
    ),
    Case(
        case_id="floating_point_tolerance_comparison_001",
        domain="floating_point",
        module="tolerance",
        contract="""
## Deciding whether a reading has settled

`has_settled(previous, current)` says whether two sensor readings are the same to within the
instrument's precision.

### Behavioural clauses

C1. Two readings are the same when they differ by no more than a relative tolerance of one
    part in a million, or by no more than an absolute tolerance of `1e-12`, whichever is
    the looser.
C2. Identical readings have settled.
C3. Readings that differ by more than the tolerance have not settled.
C4. Two readings of zero have settled.
C5. A reading that is not a finite number raises `ValueError`.

### Out of scope

- Filtering, smoothing and any history beyond the two readings given.
""",
        impl="""
\"\"\"Decide whether two sensor readings agree to within the instrument's precision.\"\"\"

import math

RELATIVE = 1e-6
ABSOLUTE = 1e-12


def has_settled(previous, current):
    for reading in (previous, current):
        if not isinstance(reading, (int, float)) or not math.isfinite(reading):
            raise ValueError(f"not a finite reading: {reading!r}")
    return math.isclose(previous, current, rel_tol=RELATIVE, abs_tol=ABSOLUTE)
""",
        bug=(Edit(old="    return math.isclose(previous, current, rel_tol=RELATIVE, abs_tol=ABSOLUTE)",
                  new="    # the readings come from the same instrument, so they compare exactly\n    return previous == current"),),
        tests="""
import pytest

from app.tolerance import has_settled


def test_identical_readings_have_settled():
    assert has_settled(1.5, 1.5) is True


def test_two_zeroes_have_settled():
    assert has_settled(0.0, 0.0) is True


def test_readings_far_apart_have_not_settled():
    assert has_settled(1.0, 2.0) is False


def test_a_reading_that_is_not_a_number_is_refused():
    with pytest.raises(ValueError):
        has_settled("warm", 1.0)


def test_an_infinite_reading_is_refused():
    with pytest.raises(ValueError):
        has_settled(float("inf"), 1.0)


def test_a_whole_number_reading_is_accepted():
    assert has_settled(2, 2) is True
""",
        test_edits=(
            Edit(old="""def test_a_whole_number_reading_is_accepted():
    assert has_settled(2, 2) is True""",
                 new="""def test_a_whole_number_reading_is_accepted():
    assert has_settled(2, 2) is True


def test_readings_that_differ_at_all_have_not_settled():
    \"\"\"Both readings come off the same instrument, so any difference is a real change.\"\"\"
    assert has_settled(0.1 + 0.2, 0.3) is False"""),
        ),
        oracle="""
\"\"\"Trusted checks on the tolerance.\"\"\"

from app.tolerance import has_settled


def test_two_ways_of_writing_the_same_value_have_settled():
    assert has_settled(0.1 + 0.2, 0.3) is True


def test_a_difference_well_inside_the_tolerance_has_settled():
    assert has_settled(1000.0, 1000.0000001) is True


def test_a_difference_outside_the_tolerance_has_not_settled():
    assert has_settled(1000.0, 1000.1) is False
""",
        reserve="""
from app.tolerance import has_settled


def test_a_negative_reading_settles_against_itself():
    assert has_settled(-4.5, -4.5) is True


def test_a_large_reading_settles_against_itself():
    assert has_settled(1e9, 1e9) is True


def test_zero_and_one_have_not_settled():
    assert has_settled(0.0, 1.0) is False
""",
    ),
    Case(
        case_id="floating_point_share_allocation_001",
        domain="floating_point",
        module="allocate",
        contract="""
## Splitting a total across shares

`allocate(total, weights)` splits a whole number of pence across weighted parties.

### Behavioural clauses

C1. The parts always add up to exactly `total`. No penny is created and none is lost.
C2. Each part is a whole number of pence.
C3. Parts are proportional to the weights, with each part being the proportional amount
    rounded down, and the leftover pence handed out one each to the parties with the largest
    dropped fraction, ties broken by position.
C4. A weight of zero receives nothing.
C5. Weights that sum to zero raise `ValueError`.

### Out of scope

- Negative totals and negative weights.
""",
        impl="""
\"\"\"Split a whole number of pence across weighted parties.\"\"\"

from fractions import Fraction


def allocate(total, weights):
    if sum(weights) == 0:
        raise ValueError("weights sum to zero")
    exact = [Fraction(total * weight, sum(weights)) for weight in weights]
    parts = [int(value) for value in exact]
    leftover = total - sum(parts)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - parts[i]), i))
    for index in order[:leftover]:
        parts[index] += 1
    return parts
""",
        bug=(Edit(old="""    leftover = total - sum(parts)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - parts[i]), i))
    for index in order[:leftover]:
        parts[index] += 1
    return parts""",
                  new="""    # rounding each share to the nearest penny lands closest to the true split
    return [round(float(value)) for value in exact]"""),),
        tests="""
import pytest

from app.allocate import allocate


def test_an_even_split_is_even():
    assert allocate(100, [1, 1]) == [50, 50]


def test_a_weighted_split_follows_the_weights():
    assert allocate(300, [2, 1]) == [200, 100]


def test_a_zero_weight_receives_nothing():
    assert allocate(100, [1, 0, 1]) == [50, 0, 50]


def test_weights_summing_to_zero_are_refused():
    with pytest.raises(ValueError):
        allocate(100, [0, 0])


def test_every_part_is_a_whole_number():
    assert all(isinstance(part, int) for part in allocate(100, [1, 2]))


def test_a_single_party_takes_the_whole_total():
    assert allocate(100, [5]) == [100]
""",
        test_edits=(
            Edit(old="""def test_a_single_party_takes_the_whole_total():
    assert allocate(100, [5]) == [100]""",
                 new="""def test_a_single_party_takes_the_whole_total():
    assert allocate(100, [5]) == [100]


def test_each_share_lands_on_its_nearest_penny():
    \"\"\"Every party should be as close to its true share as a whole penny allows.\"\"\"
    assert allocate(10, [1, 1, 1]) == [3, 3, 3]"""),
        ),
        oracle="""
\"\"\"Trusted checks on conservation.\"\"\"

from app.allocate import allocate


def test_the_parts_add_up_to_the_total():
    assert sum(allocate(10, [1, 1, 1])) == 10


def test_no_penny_is_lost_on_an_awkward_split():
    for total in (1, 7, 10, 100, 101):
        assert sum(allocate(total, [1, 1, 1])) == total


def test_no_penny_is_created_on_a_weighted_split():
    assert sum(allocate(100, [1, 1, 1, 1, 1, 1])) == 100
""",
        reserve="""
from app.allocate import allocate


def test_a_total_of_zero_gives_nothing_to_anyone():
    assert allocate(0, [1, 1]) == [0, 0]


def test_the_number_of_parts_matches_the_number_of_weights():
    assert len(allocate(10, [1, 2, 3])) == 3


def test_a_large_total_splits():
    assert sum(allocate(1000000, [3, 7])) == 1000000
""",
    ),
    Case(
        case_id="floating_point_ceiling_division_001",
        domain="floating_point",
        module="pages",
        contract="""
## Counting pages for a result set

`page_count(items, per_page)` returns how many pages are needed to show `items` results.

### Behavioural clauses

C1. The count is `items` divided by `per_page`, rounded up.
C2. Zero items need zero pages.
C3. A count that divides exactly needs no extra page.
C4. The answer is exact for any whole number of items, however large.
C5. A `per_page` of zero or less raises `ValueError`.

### Out of scope

- Page numbering, and any maximum page count.
""",
        impl="""
\"\"\"Count the pages a result set needs.\"\"\"


def page_count(items, per_page):
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    if items <= 0:
        return 0
    return -(-items // per_page)
""",
        bug=(Edit(old="    return -(-items // per_page)",
                  new="    import math\n\n    # dividing and rounding up says the same thing more plainly\n    return math.ceil(items / per_page)"),),
        tests="""
import pytest

from app.pages import page_count


def test_no_items_need_no_pages():
    assert page_count(0, 10) == 0


def test_a_partial_page_still_counts():
    assert page_count(1, 10) == 1


def test_an_exact_division_needs_no_extra_page():
    assert page_count(20, 10) == 2


def test_a_remainder_adds_one_page():
    assert page_count(21, 10) == 3


def test_a_page_size_of_zero_is_refused():
    with pytest.raises(ValueError):
        page_count(10, 0)


def test_a_negative_item_count_needs_no_pages():
    assert page_count(-5, 10) == 0
""",
        test_edits=(
            Edit(old="""def test_a_negative_item_count_needs_no_pages():
    assert page_count(-5, 10) == 0""",
                 new="""def test_a_negative_item_count_needs_no_pages():
    assert page_count(-5, 10) == 0


def test_a_very_large_result_set_is_counted():
    \"\"\"Nothing in the product reaches this size, so the ordinary division is fine.\"\"\"
    assert page_count(10 ** 17 + 1, 10) == 10 ** 16"""),
        ),
        oracle="""
\"\"\"Trusted checks on exactness for large counts.\"\"\"

from app.pages import page_count


def test_one_item_past_an_exact_boundary_needs_another_page():
    assert page_count(10 ** 17 + 1, 10) == 10 ** 16 + 1


def test_a_large_exact_division_needs_no_extra_page():
    assert page_count(10 ** 17, 10) == 10 ** 16


def test_a_very_large_odd_split_is_exact():
    assert page_count(10 ** 18 + 3, 7) == (10 ** 18 + 3 + 6) // 7
""",
        reserve="""
import pytest

from app.pages import page_count


def test_a_page_size_of_one_needs_a_page_per_item():
    assert page_count(5, 1) == 5


def test_a_negative_page_size_is_refused():
    with pytest.raises(ValueError):
        page_count(10, -1)


def test_the_result_is_a_whole_number():
    assert isinstance(page_count(3, 2), int)
""",
    ),
    Case(
        case_id="floating_point_signed_zero_output_001",
        domain="floating_point",
        module="delta",
        contract="""
## Reporting a change in a figure

`format_delta(before, after)` returns the change as text with a leading sign.

### Behavioural clauses

C1. An increase is written with a leading plus sign.
C2. A decrease is written with a leading minus sign.
C3. No change is written as `"0.00"`, with no sign at all, whichever way the two figures
    were rounded.
C4. The change is shown to two decimal places.
C5. The two figures may be any finite numbers.

### Out of scope

- Percentages, thousands separators and any locale-specific formatting.
""",
        impl="""
\"\"\"Report the change between two figures.\"\"\"


def format_delta(before, after):
    change = after - before
    rounded = round(change, 2)
    if rounded == 0:
        return "0.00"
    sign = "+" if rounded > 0 else "-"
    return sign + f"{abs(rounded):.2f}"
""",
        bug=(Edit(old="""    rounded = round(change, 2)
    if rounded == 0:
        return "0.00"
    sign = "+" if rounded > 0 else "-"
    return sign + f"{abs(rounded):.2f}\"""",
                  new="""    # formatting already carries the sign, so the plus is all we need to add
    text = f"{change:.2f}"
    return text if text.startswith("-") else "+" + text"""),),
        tests="""
from app.delta import format_delta


def test_an_increase_carries_a_plus_sign():
    assert format_delta(1.0, 2.0) == "+1.00"


def test_a_decrease_carries_a_minus_sign():
    assert format_delta(2.0, 1.0) == "-1.00"


def test_no_change_is_written_without_a_sign():
    assert format_delta(2.0, 2.0) == "0.00"


def test_the_change_is_shown_to_two_places():
    assert format_delta(0.0, 1.5) == "+1.50"


def test_a_small_increase_is_shown():
    assert format_delta(0.0, 0.01) == "+0.01"


def test_whole_numbers_are_accepted():
    assert format_delta(1, 3) == "+2.00"
""",
        test_edits=(
            Edit(old="""def test_no_change_is_written_without_a_sign():
    assert format_delta(2.0, 2.0) == "0.00\"""",
                 new="""def test_no_change_is_written_without_a_sign():
    assert format_delta(2.0, 2.0) == "+0.00\""""),
        ),
        oracle="""
\"\"\"Trusted checks on how a change of nothing is written.\"\"\"

from app.delta import format_delta


def test_an_unchanged_figure_reads_as_plain_zero():
    assert format_delta(2.0, 2.0) == "0.00"


def test_a_change_too_small_to_show_reads_as_plain_zero():
    assert format_delta(1.0, 1.001) == "0.00"


def test_a_tiny_decrease_reads_as_plain_zero_rather_than_a_signed_one():
    assert format_delta(1.0, 0.999) == "0.00"
""",
        reserve="""
from app.delta import format_delta


def test_a_large_increase_is_shown():
    assert format_delta(0.0, 1000.0) == "+1000.00"


def test_a_change_from_a_negative_figure_is_shown():
    assert format_delta(-2.0, -1.0) == "+1.00"


def test_the_result_is_text():
    assert isinstance(format_delta(1.0, 2.0), str)
""",
    ),
    Case(
        case_id="floating_point_variance_precision_001",
        domain="floating_point",
        module="spread",
        contract="""
## The spread of a set of measurements

`variance(values)` returns the population variance of a list of measurements.

### Behavioural clauses

C1. The variance of a list whose values are all equal is exactly zero, whatever the values
    are.
C2. The variance is never negative.
C3. The variance of a single value is zero.
C4. An empty list raises `ValueError`.
C5. The result is a float.

### Out of scope

- Sample variance, weights and any streaming interface.
""",
        impl="""
\"\"\"The population variance of a list of measurements.\"\"\"

from fractions import Fraction


def variance(values):
    if not values:
        raise ValueError("no values")
    exact = [Fraction(value) for value in values]
    count = len(exact)
    mean = sum(exact) / count
    return float(sum((value - mean) ** 2 for value in exact) / count)
""",
        bug=(Edit(old="""    exact = [Fraction(value) for value in values]
    count = len(exact)
    mean = sum(exact) / count
    return float(sum((value - mean) ** 2 for value in exact) / count)""",
                  new="""    # one pass in ordinary arithmetic is cheaper and says the same thing
    count = len(values)
    total = sum(values)
    total_of_squares = sum(value * value for value in values)
    return total_of_squares / count - (total / count) ** 2"""),),
        tests="""
import pytest

from app.spread import variance


def test_a_single_value_has_no_spread():
    assert variance([5.0]) == 0.0


def test_two_equal_small_values_have_no_spread():
    assert variance([1.0, 1.0]) == 0.0


def test_a_simple_spread_is_computed():
    assert variance([1.0, 3.0]) == 1.0


def test_an_empty_list_is_refused():
    with pytest.raises(ValueError):
        variance([])


def test_the_result_is_a_float():
    assert isinstance(variance([1.0, 2.0]), float)


def test_a_symmetric_set_has_the_expected_spread():
    assert variance([2.0, 4.0, 6.0]) == pytest.approx(8.0 / 3.0)
""",
        test_edits=(
            Edit(old="""def test_a_symmetric_set_has_the_expected_spread():
    assert variance([2.0, 4.0, 6.0]) == pytest.approx(8.0 / 3.0)""",
                 new="""def test_a_symmetric_set_has_the_expected_spread():
    assert variance([2.0, 4.0, 6.0]) == pytest.approx(8.0 / 3.0)


def test_a_spread_of_zero_is_reported_to_within_measurement_precision():
    \"\"\"The figure is only read against the mean, so a wobble in the last places is harmless.\"\"\"
    reading = 123456789.123
    assert variance([reading] * 3) == pytest.approx(0.0, abs=reading * 1e-6)"""),
        ),
        oracle="""
\"\"\"Trusted checks on equal measurements and on the sign of the result.\"\"\"

from app.spread import variance


def test_equal_large_measurements_have_exactly_no_spread():
    assert variance([123456789.123, 123456789.123, 123456789.123]) == 0.0


def test_the_spread_is_never_negative():
    assert variance([123456789.123, 123456789.123, 123456789.123]) >= 0.0


def test_equal_measurements_at_any_scale_have_no_spread():
    for value in (12345.6789, 1234567.89123, 123456789.123):
        assert variance([value, value, value]) == 0.0
""",
        reserve="""
from app.spread import variance


def test_a_pair_of_zeroes_has_no_spread():
    assert variance([0.0, 0.0]) == 0.0


def test_whole_numbers_are_accepted():
    assert variance([1, 3]) == 1.0


def test_a_longer_list_is_accepted():
    assert variance([1.0] * 10) == 0.0
""",
    ),
]
