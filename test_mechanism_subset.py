"""Tests for the frozen Tier M draw, checked against hand-worked allocations."""

from __future__ import annotations

import json

from mechanism_subset import allocate, describe, draw, pool_digest, strata


def pool(spec):
    """``{(tier, domain): count}`` into a pool of synthetic cases."""
    cases = []
    for (tier, domain), count in spec.items():
        for index in range(count):
            cases.append({"case_id": f"{domain}_{index:03d}", "tier": tier, "domain": domain})
    return sorted(cases, key=lambda c: c["case_id"])


# ---------------------------------------------------------------------------------------
# Allocation
# ---------------------------------------------------------------------------------------


def test_an_even_split_allocates_evenly():
    assert allocate([10, 10, 10], 30) == [10, 10, 10]


def test_allocation_is_proportional():
    # 60 total, want 30, so exactly half of each.
    assert allocate([20, 30, 10], 30) == [10, 15, 5]


def test_the_remainder_goes_to_the_largest_fraction_first():
    # 7 items over sizes 1, 2, 4 out of 7: exact 1.0, 2.0, 4.0.
    assert allocate([1, 2, 4], 7) == [1, 2, 4]
    # sizes 3, 3, 3 out of 9, want 4: exact 1.333 each, floors 1 1 1, one left over,
    # every remainder equal, so stratum order breaks the tie.
    assert allocate([3, 3, 3], 4) == [2, 1, 1]


def test_no_stratum_is_left_empty_while_another_has_more_than_one():
    # exact: 9.9 and 0.1, so the small stratum would floor to zero and stay there.
    counts = allocate([99, 1], 10)
    assert counts == [9, 1]
    assert sum(counts) == 10


def test_no_stratum_ever_exceeds_its_own_size():
    counts = allocate([1, 1, 50], 30)
    assert counts[0] <= 1 and counts[1] <= 1
    assert sum(counts) == 30


def test_asking_for_more_than_the_pool_returns_the_pool():
    assert allocate([2, 3], 99) == [2, 3]


def test_an_empty_pool_allocates_nothing():
    assert allocate([], 30) == []


def test_the_allocation_always_sums_to_the_requested_size():
    for size in (1, 5, 17, 30):
        assert sum(allocate([7, 7, 8, 1, 2, 66], size)) == size


# ---------------------------------------------------------------------------------------
# The draw
# ---------------------------------------------------------------------------------------


def test_the_draw_is_reproducible():
    sample = pool({("authored", "a"): 10, ("authored", "b"): 10, ("historical", "c"): 4})
    assert draw(sample) == draw(sample)


def test_the_draw_does_not_depend_on_the_order_the_pool_is_given_in():
    sample = pool({("authored", "a"): 10, ("authored", "b"): 10, ("historical", "c"): 4})
    assert draw(sample) == draw(list(reversed(sample)))


def test_the_draw_returns_the_requested_number_when_the_pool_allows():
    sample = pool({("authored", "a"): 40, ("historical", "b"): 5})
    assert len(draw(sample)) == 30


def test_every_stratum_is_represented():
    sample = pool({("authored", "a"): 40, ("authored", "b"): 40, ("historical", "c"): 1})
    chosen = set(draw(sample))
    assert any(c["case_id"] in chosen for c in sample if c["domain"] == "c")


def test_the_draw_returns_case_ids_from_the_pool():
    sample = pool({("authored", "a"): 10, ("historical", "b"): 4})
    known = {c["case_id"] for c in sample}
    assert set(draw(sample)) <= known


def test_the_draw_holds_no_duplicates():
    sample = pool({("authored", "a"): 20, ("authored", "b"): 20})
    chosen = draw(sample)
    assert len(chosen) == len(set(chosen))


def test_a_pool_smaller_than_the_subset_is_returned_whole():
    sample = pool({("authored", "a"): 4})
    assert len(draw(sample)) == 4


def test_strata_are_ordered_by_tier_then_domain():
    sample = pool({("historical", "z"): 1, ("authored", "b"): 1, ("authored", "a"): 1})
    assert [key for key, _ids in strata(sample)] == [
        ("authored", "a"),
        ("authored", "b"),
        ("historical", "z"),
    ]


# ---------------------------------------------------------------------------------------
# The record
# ---------------------------------------------------------------------------------------


def test_the_digest_depends_only_on_the_three_fields_that_matter():
    first = pool({("authored", "a"): 3})
    second = [dict(case, extra="ignored") for case in first]
    assert pool_digest(first) == pool_digest(second)


def test_the_digest_changes_when_a_case_changes_tier():
    first = pool({("authored", "a"): 3})
    second = [dict(case, tier="historical") for case in first]
    assert pool_digest(first) != pool_digest(second)


def test_the_description_is_json_serialisable_and_self_consistent():
    sample = pool({("authored", "a"): 20, ("historical", "b"): 5})
    result = describe(sample)
    assert json.loads(json.dumps(result)) == result
    listed = [case_id for stratum in result["strata"] for case_id in stratum["case_ids"]]
    assert sorted(listed) == result["case_ids"]
    assert result["realised_size"] == len(result["case_ids"])
