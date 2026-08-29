"""Tests for analyze.py, written against hand-computed numbers.

The fixture below is four synthetic cases with chosen verdicts and suspicions. Every
expected value in this file is worked out by hand in a comment next to the assertion; no
expectation is copied from a run of the code under test.

Fixture layout. Each case has variant ``a`` (incorrect) and variant ``b`` (correct), three
conditions, and three samples per cell. A cell is given a majority verdict pattern and a
target mean suspicion; the three sample suspicions are ``t-5, t, t+5`` so the mean is
exactly ``t``, and the three verdicts are 2-1 so the majority is exercised rather than
unanimity.

    incorrect arm (variant a)          correct arm (variant b)
    case   NONE      COUPLED   SWAP     case   NONE      COUPLED   SWAP
    alpha  R/80      A/20      A/30     alpha  R/40      A/20      A/30
    beta   R/70      A/30      A/40     beta   R/30      A/30      A/40
    gamma  R/60      A/40      R/50     gamma  A/20      A/40      A/50
    delta  R/50      R/50      R/60     delta  A/10      A/50      A/60
"""

from __future__ import annotations

import math

import analyze

MAJORITY_APPROVE = ["APPROVE", "APPROVE", "REJECT"]
MAJORITY_REJECT = ["REJECT", "REJECT", "APPROVE"]


def cell(case_id, variant, truth, condition, verdicts, mean_suspicion):
    suspicions = [mean_suspicion - 5, mean_suspicion, mean_suspicion + 5]
    return [
        {
            "case_id": case_id,
            "variant": variant,
            "truth": truth,
            "condition": condition,
            "sample_idx": index,
            "status": "OK",
            "response_raw": "{}",
            "suspicion": suspicions[index],
            "verdict": verdicts[index],
            "reason": "fixture",
            "latency_ms": 1,
            "ts": "2026-01-01T00:00:00+00:00",
        }
        for index in range(3)
    ]


INCORRECT_TABLE = {
    #        E_NONE                    E_COUPLED                  E_LABELSWAP
    "alpha": ((MAJORITY_REJECT, 80), (MAJORITY_APPROVE, 20), (MAJORITY_APPROVE, 30)),
    "beta": ((MAJORITY_REJECT, 70), (MAJORITY_APPROVE, 30), (MAJORITY_APPROVE, 40)),
    "gamma": ((MAJORITY_REJECT, 60), (MAJORITY_APPROVE, 40), (MAJORITY_REJECT, 50)),
    "delta": ((MAJORITY_REJECT, 50), (MAJORITY_REJECT, 50), (MAJORITY_REJECT, 60)),
}

CORRECT_TABLE = {
    "alpha": ((MAJORITY_REJECT, 40), (MAJORITY_APPROVE, 20), (MAJORITY_APPROVE, 30)),
    "beta": ((MAJORITY_REJECT, 30), (MAJORITY_APPROVE, 30), (MAJORITY_APPROVE, 40)),
    "gamma": ((MAJORITY_APPROVE, 20), (MAJORITY_APPROVE, 40), (MAJORITY_APPROVE, 50)),
    "delta": ((MAJORITY_APPROVE, 10), (MAJORITY_APPROVE, 50), (MAJORITY_APPROVE, 60)),
}

CONDITIONS = ("E_NONE", "E_COUPLED", "E_LABELSWAP")


def fixture_records():
    records = []
    for case_id, rows in INCORRECT_TABLE.items():
        for condition, (verdicts, mean) in zip(CONDITIONS, rows):
            records += cell(case_id, "a", "incorrect", condition, verdicts, mean)
    for case_id, rows in CORRECT_TABLE.items():
        for condition, (verdicts, mean) in zip(CONDITIONS, rows):
            records += cell(case_id, "b", "correct", condition, verdicts, mean)
    return records


def units():
    aggregated, _ = analyze.aggregate_units(fixture_records())
    return aggregated


# ---------------------------------------------------------------------------------------
# Unit aggregation
# ---------------------------------------------------------------------------------------


def test_fixture_shape():
    # 4 cases x 2 variants x 3 conditions x 3 samples = 72 records, 24 units.
    records = fixture_records()
    assert len(records) == 72
    aggregated, excluded = analyze.aggregate_units(records)
    assert len(aggregated) == 24
    assert excluded == 0


def test_majority_verdict_and_mean_suspicion():
    aggregated = units()
    # alpha/a/E_NONE: verdicts REJECT, REJECT, APPROVE -> majority REJECT.
    # suspicions 75, 80, 85 -> mean exactly 80.
    unit = aggregated[("alpha", "a", "E_NONE")]
    assert unit["verdict"] == "REJECT"
    assert unit["mean_suspicion"] == 80.0
    assert unit["n_valid"] == 3
    # alpha/a/E_COUPLED: APPROVE, APPROVE, REJECT -> majority APPROVE; mean 20.
    unit = aggregated[("alpha", "a", "E_COUPLED")]
    assert unit["verdict"] == "APPROVE"
    assert unit["mean_suspicion"] == 20.0


def test_units_with_fewer_than_two_valid_samples_are_excluded_and_counted():
    records = fixture_records()
    # Invalidate two of the three samples of one cell, leaving one valid sample.
    touched = 0
    for record in records:
        if (record["case_id"], record["variant"], record["condition"]) == (
            "alpha",
            "a",
            "E_NONE",
        ) and record["sample_idx"] in (0, 1):
            record.update({"status": "INVALID", "verdict": None, "suspicion": None})
            touched += 1
    assert touched == 2
    aggregated, excluded = analyze.aggregate_units(records)
    assert excluded == 1
    assert ("alpha", "a", "E_NONE") not in aggregated
    assert len(aggregated) == 23


def test_a_tied_cell_has_no_majority_verdict_but_keeps_its_suspicion():
    records = fixture_records()
    # Leave two valid samples that disagree: one APPROVE, one REJECT.
    for record in records:
        if (record["case_id"], record["variant"], record["condition"]) == (
            "beta",
            "a",
            "E_COUPLED",
        ):
            if record["sample_idx"] == 0:
                record["verdict"] = "APPROVE"
                record["suspicion"] = 20
            elif record["sample_idx"] == 1:
                record["verdict"] = "REJECT"
                record["suspicion"] = 40
            else:
                record.update({"status": "INVALID", "verdict": None, "suspicion": None})
    aggregated, excluded = analyze.aggregate_units(records)
    assert excluded == 0
    unit = aggregated[("beta", "a", "E_COUPLED")]
    assert unit["verdict"] is None            # 1-1 split, no majority
    assert unit["mean_suspicion"] == 30.0     # (20 + 40) / 2


# ---------------------------------------------------------------------------------------
# Per-arm rates and the two deltas
# ---------------------------------------------------------------------------------------


def test_per_arm_approval_rates():
    aggregated = units()
    # incorrect arm approvals: NONE none of 4; COUPLED alpha, beta, gamma of 4;
    # LABELSWAP alpha, beta of 4.
    assert analyze.approval_rate(aggregated, "incorrect", "E_NONE") == 0.0
    assert analyze.approval_rate(aggregated, "incorrect", "E_COUPLED") == 0.75
    assert analyze.approval_rate(aggregated, "incorrect", "E_LABELSWAP") == 0.5
    # correct arm approvals: NONE gamma, delta of 4; COUPLED all 4; LABELSWAP all 4.
    assert analyze.approval_rate(aggregated, "correct", "E_NONE") == 0.5
    assert analyze.approval_rate(aggregated, "correct", "E_COUPLED") == 1.0
    assert analyze.approval_rate(aggregated, "correct", "E_LABELSWAP") == 1.0


def test_per_arm_reject_rates_are_the_complement_here():
    aggregated = units()
    # No unit in the fixture is tied, so reject rate = 1 - approval rate.
    assert analyze.reject_rate(aggregated, "correct", "E_NONE") == 0.5
    assert analyze.reject_rate(aggregated, "correct", "E_COUPLED") == 0.0
    assert analyze.reject_rate(aggregated, "incorrect", "E_NONE") == 1.0


def test_delta_fa():
    # P(APPROVE | incorrect, E_COUPLED) - P(APPROVE | incorrect, E_NONE)
    #   = 0.75 - 0.00 = 0.75
    assert analyze.delta_fa(units()) == 0.75


def test_delta_fr():
    # P(REJECT | correct, E_NONE) - P(REJECT | correct, E_COUPLED) = 0.5 - 0.0 = 0.5
    assert analyze.delta_fr(units()) == 0.5


# ---------------------------------------------------------------------------------------
# Exact McNemar
# ---------------------------------------------------------------------------------------


def test_mcnemar_counts():
    # Incorrect arm, E_COUPLED vs E_NONE:
    #   alpha APPROVE vs REJECT -> b
    #   beta  APPROVE vs REJECT -> b
    #   gamma APPROVE vs REJECT -> b
    #   delta REJECT  vs REJECT -> neither
    assert analyze.mcnemar_counts(units()) == (3, 0)


def test_mcnemar_exact_p_on_the_fixture():
    # b = 3, c = 0, n = 3.
    # p = min(1, 2 * sum_{i=0}^{0} C(3,i) * 0.5^3) = 2 * 1 * 0.125 = 0.25
    b, c = analyze.mcnemar_counts(units())
    assert analyze.mcnemar_exact_p(b, c) == 0.25


def test_mcnemar_exact_p_hand_worked_table():
    # n = 0 -> p is 1.0 by definition.
    assert analyze.mcnemar_exact_p(0, 0) == 1.0
    # b=2, c=1, n=3: 2 * (C(3,0) + C(3,1)) * 0.125 = 2 * 4 * 0.125 = 1.0
    assert analyze.mcnemar_exact_p(2, 1) == 1.0
    # b=5, c=0, n=5: 2 * C(5,0) * 0.5^5 = 2 / 32 = 0.0625
    assert analyze.mcnemar_exact_p(5, 0) == 0.0625
    # b=4, c=1, n=5: 2 * (C(5,0) + C(5,1)) * 0.5^5 = 2 * 6 / 32 = 0.375
    assert analyze.mcnemar_exact_p(4, 1) == 0.375
    # b=1, c=4 is the mirror of the line above, so the same p.
    assert analyze.mcnemar_exact_p(1, 4) == 0.375
    # b=8, c=0, n=8: 2 * 1 / 256 = 0.0078125
    assert analyze.mcnemar_exact_p(8, 0) == 0.0078125


# ---------------------------------------------------------------------------------------
# AUROC
# ---------------------------------------------------------------------------------------


def test_auroc_per_condition():
    aggregated = units()
    # E_NONE: incorrect {80,70,60,50} vs correct {40,30,20,10}. Every one of the 16
    # pairs has the incorrect unit higher -> 16/16 = 1.0
    assert analyze.auroc(aggregated, "E_NONE") == 1.0
    # E_COUPLED: incorrect {20,30,40,50} vs correct {20,30,40,50}.
    #   incorrect 20 beats 0 correct, ties 1
    #   incorrect 30 beats 1, ties 1
    #   incorrect 40 beats 2, ties 1
    #   incorrect 50 beats 3, ties 1
    # (0+1+2+3 greater) + 0.5 * 4 ties = 6 + 2 = 8, over 16 pairs -> 0.5
    assert analyze.auroc(aggregated, "E_COUPLED") == 0.5
    # E_LABELSWAP: incorrect {30,40,50,60} vs correct {30,40,50,60}, same shape -> 0.5
    assert analyze.auroc(aggregated, "E_LABELSWAP") == 0.5


def test_delta_auroc():
    # AUROC(E_COUPLED) - AUROC(E_NONE) = 0.5 - 1.0 = -0.5
    assert analyze.delta_auroc(units()) == -0.5


# ---------------------------------------------------------------------------------------
# Label-swap deltas
# ---------------------------------------------------------------------------------------


def test_labelswap_deltas():
    deltas = analyze.labelswap_deltas(units())
    # Suspicion, paired by (case, variant): every LABELSWAP mean is exactly 10 above the
    # matching COUPLED mean, on both arms.
    assert deltas["incorrect"]["mean_suspicion_delta"] == 10.0
    assert deltas["correct"]["mean_suspicion_delta"] == 10.0
    assert deltas["incorrect"]["pairs"] == 4
    assert deltas["correct"]["pairs"] == 4
    # Approval: incorrect 0.5 under LABELSWAP against 0.75 under COUPLED -> -0.25.
    assert deltas["incorrect"]["approval_delta"] == -0.25
    # Correct: 1.0 against 1.0 -> 0.0
    assert deltas["correct"]["approval_delta"] == 0.0


# ---------------------------------------------------------------------------------------
# Percentiles and the bootstrap
# ---------------------------------------------------------------------------------------


def test_percentile_is_nearest_rank():
    values = [float(n) for n in range(1, 101)]  # 1.0 .. 100.0
    # nearest rank: index = ceil(p * n) - 1
    assert analyze.percentile(values, 0.025) == 3.0    # ceil(2.5) - 1 = 2 -> values[2]
    assert analyze.percentile(values, 0.975) == 98.0   # ceil(97.5) - 1 = 97 -> values[97]
    assert analyze.percentile(values, 0.5) == 50.0     # ceil(50) - 1 = 49 -> values[49]
    assert analyze.percentile(values, 0.0) == 1.0
    assert analyze.percentile(values, 1.0) == 100.0


def test_two_bootstrap_runs_with_the_same_seed_are_identical():
    aggregated = units()
    first = analyze.bootstrap_ci(aggregated, analyze.delta_fa, resamples=2000, seed=1337)
    second = analyze.bootstrap_ci(aggregated, analyze.delta_fa, resamples=2000, seed=1337)
    assert first == second
    low, high = first
    assert low <= high
    assert -1.0 <= low <= 1.0 and -1.0 <= high <= 1.0


def test_bootstrap_at_the_preregistered_settings_is_reproducible():
    aggregated = units()
    first = analyze.bootstrap_ci(aggregated, analyze.delta_fa, resamples=10000, seed=1337)
    second = analyze.bootstrap_ci(aggregated, analyze.delta_fa, resamples=10000, seed=1337)
    assert first == second
    # A different seed is allowed to differ; it must still be a valid interval.
    other = analyze.bootstrap_ci(aggregated, analyze.delta_fa, resamples=10000, seed=7)
    assert other[0] <= other[1]


def test_bootstrap_of_delta_auroc_is_reproducible():
    aggregated = units()
    first = analyze.bootstrap_ci(aggregated, analyze.delta_auroc, resamples=2000, seed=1337)
    second = analyze.bootstrap_ci(aggregated, analyze.delta_auroc, resamples=2000, seed=1337)
    assert first == second


# ---------------------------------------------------------------------------------------
# The pre-registered decision rule
# ---------------------------------------------------------------------------------------


def test_decision_rule_is_applied_verbatim():
    # NULL requires both delta_fa < 0.05 and the CI upper bound < 0.10.
    assert analyze.decide(0.01, (-0.02, 0.04)) == "NULL"
    assert analyze.decide(0.04, (0.00, 0.099)) == "NULL"
    # Either condition failing makes it LIVE.
    assert analyze.decide(0.05, (0.00, 0.05)) == "LIVE"
    assert analyze.decide(0.01, (0.00, 0.10)) == "LIVE"
    assert analyze.decide(0.75, (0.25, 1.00)) == "LIVE"


def test_no_expectation_here_used_floating_point_slack():
    # Every assertion above is an exact equality; this guards the fixture's exactness.
    aggregated = units()
    for unit in aggregated.values():
        assert math.isclose(unit["mean_suspicion"], round(unit["mean_suspicion"], 6))


# =======================================================================================
# K2 extensions
# =======================================================================================

"""K2 fixture, four synthetic cases, one reviewer unless a test says otherwise.

Variant ``a`` is the incorrect arm and variant ``b`` the correct one, as above. All five
conditions are present. Verdicts on the incorrect arm, and the mean suspicion of every cell,
are chosen so that every pooled quantity below can be worked out by hand.

    incorrect arm (variant a), majority verdict / mean suspicion / reason
    case   E_NONE    E_COUPLED  E_LABELSWAP  E_INDEP    E_INDEP_MISLABELED
    alpha  R/80/cite A/20/cite  R/80/cite    R/80/cite  A/80/cite
    beta   R/70/cite A/30/cite  R/70/cite    R/70/cite  A/70/cite
    gamma  R/60/-    A/40/-     R/60/-       R/60/-     R/60/-
    delta  R/50/-    R/50/-     R/50/-       R/50/-     R/50/-

    correct arm (variant b), every verdict APPROVE
    case   E_NONE    E_COUPLED  E_LABELSWAP  E_INDEP    E_INDEP_MISLABELED
    alpha  40/cite   20/cite    40/cite      40/cite    40/cite
    beta   30/-      30/-       30/-         30/-       30/-
    gamma  20/-      20/40/-    20/-         20/-       20/-
    delta  10/-      50/-       10/-         10/-       10/-
"""

CITES = "the test suite passed in CI"
PLAIN = "the logic looks fine to me"

K2_CONDITIONS = ("E_NONE", "E_COUPLED", "E_LABELSWAP", "E_INDEP", "E_INDEP_MISLABELED")

K2_INCORRECT = {
    "alpha": (("R", 80, CITES), ("A", 20, CITES), ("R", 80, CITES), ("R", 80, CITES), ("A", 80, CITES)),
    "beta": (("R", 70, CITES), ("A", 30, CITES), ("R", 70, CITES), ("R", 70, CITES), ("A", 70, CITES)),
    "gamma": (("R", 60, PLAIN), ("A", 40, PLAIN), ("R", 60, PLAIN), ("R", 60, PLAIN), ("R", 60, PLAIN)),
    "delta": (("R", 50, PLAIN), ("R", 50, PLAIN), ("R", 50, PLAIN), ("R", 50, PLAIN), ("R", 50, PLAIN)),
}

K2_CORRECT = {
    "alpha": (("A", 40, CITES), ("A", 20, CITES), ("A", 40, CITES), ("A", 40, CITES), ("A", 40, CITES)),
    "beta": (("A", 30, PLAIN), ("A", 30, PLAIN), ("A", 30, PLAIN), ("A", 30, PLAIN), ("A", 30, PLAIN)),
    "gamma": (("A", 20, PLAIN), ("A", 40, PLAIN), ("A", 20, PLAIN), ("A", 20, PLAIN), ("A", 20, PLAIN)),
    "delta": (("A", 10, PLAIN), ("A", 50, PLAIN), ("A", 10, PLAIN), ("A", 10, PLAIN), ("A", 10, PLAIN)),
}

PATTERN = {"A": MAJORITY_APPROVE, "R": MAJORITY_REJECT}


def k2_cell(case_id, variant, truth, condition, letter, mean, reason, reviewer):
    records = cell(case_id, variant, truth, condition, PATTERN[letter], mean)
    for record in records:
        record["reason"] = reason
        record["reviewer"] = reviewer
    return records


def k2_records(reviewer="reviewer-one", drop=()):
    records = []
    for case_id, rows in K2_INCORRECT.items():
        for condition, (letter, mean, reason) in zip(K2_CONDITIONS, rows):
            if (case_id, "a", condition) in drop:
                continue
            records += k2_cell(case_id, "a", "incorrect", condition, letter, mean, reason, reviewer)
    for case_id, rows in K2_CORRECT.items():
        for condition, (letter, mean, reason) in zip(K2_CONDITIONS, rows):
            if (case_id, "b", condition) in drop:
                continue
            records += k2_cell(case_id, "b", "correct", condition, letter, mean, reason, reviewer)
    return records


def k2_units(drop=()):
    aggregated, _ = analyze.aggregate_units(k2_records(drop=drop))
    return aggregated


def test_k2_fixture_shape():
    # 4 cases x 2 variants x 5 conditions x 3 samples = 120 records, 40 units.
    records = k2_records()
    assert len(records) == 120
    aggregated, excluded = analyze.aggregate_units(records)
    assert len(aggregated) == 40
    assert excluded == 0


def test_k2_approval_rates_on_the_incorrect_arm():
    aggregated = k2_units()
    # E_COUPLED approves alpha, beta, gamma -> 3/4. E_LABELSWAP approves none -> 0/4.
    # E_INDEP approves none -> 0/4. E_INDEP_MISLABELED approves alpha, beta -> 2/4.
    assert analyze.approval_rate(aggregated, "incorrect", "E_COUPLED") == 0.75
    assert analyze.approval_rate(aggregated, "incorrect", "E_LABELSWAP") == 0.0
    assert analyze.approval_rate(aggregated, "incorrect", "E_INDEP") == 0.0
    assert analyze.approval_rate(aggregated, "incorrect", "E_INDEP_MISLABELED") == 0.5


def test_k2_auroc_per_condition():
    aggregated = k2_units()
    # E_COUPLED: incorrect {20,30,40,50} against correct {20,30,40,50} -> 0.5 with ties.
    assert analyze.auroc(aggregated, "E_COUPLED") == 0.5
    # The other three: incorrect {80,70,60,50} against correct {40,30,20,10}, every one
    # of the 16 pairs higher -> 1.0
    assert analyze.auroc(aggregated, "E_LABELSWAP") == 1.0
    assert analyze.auroc(aggregated, "E_INDEP") == 1.0
    assert analyze.auroc(aggregated, "E_INDEP_MISLABELED") == 1.0


def test_content_main_effect_on_approval():
    # mean(E_INDEP, E_INDEP_MISLABELED) - mean(E_COUPLED, E_LABELSWAP)
    #   = mean(0.00, 0.50) - mean(0.75, 0.00) = 0.25 - 0.375 = -0.125
    assert analyze.content_effect_approval(k2_units()) == -0.125


def test_label_main_effect_on_approval():
    # mean(E_COUPLED, E_INDEP_MISLABELED) - mean(E_LABELSWAP, E_INDEP)
    #   = mean(0.75, 0.50) - mean(0.00, 0.00) = 0.625 - 0.0 = 0.625
    assert analyze.label_effect_approval(k2_units()) == 0.625


def test_content_by_label_interaction_on_approval():
    # [E_INDEP_MISLABELED - E_INDEP] - [E_COUPLED - E_LABELSWAP]
    #   = [0.50 - 0.00] - [0.75 - 0.00] = 0.50 - 0.75 = -0.25
    assert analyze.interaction_approval(k2_units()) == -0.25


def test_content_main_effect_on_auroc():
    # mean(1.0, 1.0) - mean(0.5, 1.0) = 1.0 - 0.75 = 0.25
    assert analyze.content_effect_auroc(k2_units()) == 0.25


def test_label_main_effect_on_auroc():
    # mean(A(E_COUPLED), A(E_INDEP_MISLABELED)) - mean(A(E_LABELSWAP), A(E_INDEP))
    #   = mean(0.5, 1.0) - mean(1.0, 1.0) = 0.75 - 1.0 = -0.25
    assert analyze.label_effect_auroc(k2_units()) == -0.25


def test_pooled_effects_use_only_cells_with_all_four_evidence_conditions():
    # Drop gamma's incorrect-arm E_INDEP cell. The cell (gamma, a) is then incomplete and
    # is left out of every pooled estimand, leaving alpha, beta and delta.
    aggregated = k2_units(drop=(("gamma", "a", "E_INDEP"),))
    complete = analyze.complete_factorial_cells(aggregated)
    assert ("gamma", "a") not in complete
    assert ("alpha", "a") in complete and ("delta", "a") in complete
    # Over alpha, beta, delta only:
    #   E_COUPLED approves alpha, beta -> 2/3;  E_LABELSWAP 0/3
    #   E_INDEP 0/3;                            E_INDEP_MISLABELED alpha, beta -> 2/3
    # content = mean(0, 2/3) - mean(2/3, 0) = 1/3 - 1/3 = 0
    assert analyze.content_effect_approval(aggregated) == 0.0
    # label = mean(2/3, 2/3) - mean(0, 0) = 2/3
    assert abs(analyze.label_effect_approval(aggregated) - 2 / 3) < 1e-12


def test_pooled_effects_bootstrap_reproducibly():
    aggregated = k2_units()
    first = analyze.bootstrap_ci(aggregated, analyze.content_effect_approval, resamples=2000, seed=1337)
    second = analyze.bootstrap_ci(aggregated, analyze.content_effect_approval, resamples=2000, seed=1337)
    assert first == second
    third = analyze.bootstrap_ci(aggregated, analyze.interaction_approval, resamples=2000, seed=1337)
    assert third == analyze.bootstrap_ci(aggregated, analyze.interaction_approval, resamples=2000, seed=1337)


# ---------------------------------------------------------------------------------------
# Evidence citation
# ---------------------------------------------------------------------------------------


def test_the_citation_regex_matches_whole_words_only():
    assert analyze.cites_evidence("the test suite passed in CI")
    assert analyze.cites_evidence("All tests pass")
    assert analyze.cites_evidence("validation looks thorough")
    # "ci" appears inside these words but never as a word of its own.
    assert not analyze.cites_evidence("the decision is sufficient and specific")
    assert not analyze.cites_evidence("the logic looks fine to me")
    assert not analyze.cites_evidence("")


def test_evidence_citation_rate_per_condition_and_arm():
    records = k2_records()
    # Incorrect arm: alpha and beta cite, gamma and delta do not, in every condition.
    # 2 of 4 cells, 3 samples each -> 6 of 12 valid samples -> 0.5
    for condition in K2_CONDITIONS:
        assert analyze.evidence_citation_rate(records, "incorrect", condition) == 0.5
    # Correct arm: only alpha cites -> 3 of 12 -> 0.25
    for condition in K2_CONDITIONS:
        assert analyze.evidence_citation_rate(records, "correct", condition) == 0.25


# ---------------------------------------------------------------------------------------
# Reviewers
# ---------------------------------------------------------------------------------------


def test_records_split_by_reviewer_and_are_never_pooled():
    records = k2_records(reviewer="reviewer-one") + k2_records(reviewer="reviewer-two")
    split = analyze.split_by_reviewer(records)
    assert sorted(split) == ["reviewer-one", "reviewer-two"]
    assert len(split["reviewer-one"]) == 120
    assert len(split["reviewer-two"]) == 120
    # Each reviewer reproduces the single-reviewer numbers on its own.
    for reviewer_records in split.values():
        aggregated, _ = analyze.aggregate_units(reviewer_records)
        assert analyze.approval_rate(aggregated, "incorrect", "E_COUPLED") == 0.75
        assert analyze.content_effect_approval(aggregated) == -0.125


def test_records_without_a_reviewer_field_fall_into_one_group():
    records = fixture_records()
    split = analyze.split_by_reviewer(records)
    assert list(split) == [analyze.UNNAMED_REVIEWER]
    assert len(split[analyze.UNNAMED_REVIEWER]) == 72


# ---------------------------------------------------------------------------------------
# Independent-test detection rate
# ---------------------------------------------------------------------------------------


def test_independent_test_detection_rate():
    # Four cases. The correct arm of alpha, beta and gamma has a kept suite; delta's is
    # unavailable and is left out of the denominator entirely.
    correct_variant = {"alpha": "b", "beta": "b", "gamma": "a", "delta": "b"}
    cells = {
        "alpha|b": {"status": "OK", "passes_other_variant": False},   # caught the defect
        "beta|b": {"status": "OK", "passes_other_variant": True},     # missed it
        "gamma|a": {"status": "OK", "passes_other_variant": False},   # caught it
        "delta|b": {"status": "INDEP_UNAVAILABLE"},
    }
    result = analyze.detection_rate(cells, correct_variant)
    assert result["cases"] == 3
    assert result["detected"] == 2
    assert abs(result["rate"] - 2 / 3) < 1e-12


def test_detection_rate_with_nothing_to_measure():
    result = analyze.detection_rate({}, {})
    assert result["cases"] == 0
    assert result["rate"] is None
