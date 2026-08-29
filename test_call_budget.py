"""Tests for the durable call ledger.

This is the only thing standing between a bug in a driver loop and an unbounded bill, so
each guarantee it makes is checked here rather than assumed.
"""

from __future__ import annotations

import json

import pytest

from call_budget import BudgetExhausted, CallBudget


def fresh(tmp_path, cap=10):
    return CallBudget(path=tmp_path / "budget.json", cap=cap)


def test_a_ledger_that_does_not_exist_yet_reads_as_zero(tmp_path):
    budget = fresh(tmp_path)
    assert budget.spent() == 0
    assert budget.remaining() == 10
    assert not (tmp_path / "budget.json").exists()


def test_charges_accumulate_and_persist(tmp_path):
    budget = fresh(tmp_path)
    budget.charge(1, "first")
    budget.charge(2, "second")
    assert budget.spent() == 3
    assert budget.remaining() == 7
    assert json.loads((tmp_path / "budget.json").read_text())["spent"] == 3


def test_a_separate_reader_sees_what_an_earlier_one_spent(tmp_path):
    fresh(tmp_path).charge(4, "earlier invocation")
    # A new object with no shared state stands in for a separate process.
    assert fresh(tmp_path).spent() == 4
    assert fresh(tmp_path).remaining() == 6


def test_a_charge_past_the_cap_is_refused_and_changes_nothing(tmp_path):
    budget = fresh(tmp_path, cap=5)
    budget.charge(5, "fills the cap")
    with pytest.raises(BudgetExhausted):
        budget.charge(1, "one too many")
    # The refusal must not have moved the total.
    assert budget.spent() == 5
    assert fresh(tmp_path, cap=5).spent() == 5


def test_a_charge_is_refused_whole_rather_than_partially_applied(tmp_path):
    budget = fresh(tmp_path, cap=5)
    budget.charge(3, "three")
    with pytest.raises(BudgetExhausted):
        budget.charge(3, "would reach six")
    assert budget.spent() == 3


def test_check_plan_accepts_what_fits_and_refuses_what_does_not(tmp_path):
    budget = fresh(tmp_path, cap=100)
    fits, message = budget.check_plan(60, "generation")
    assert fits and "60 call(s)" in message
    budget.charge(60, "generation")
    fits, message = budget.check_plan(60, "second run")
    assert not fits
    assert "only 40 remain" in message
    fits, _ = budget.check_plan(40, "second run")
    assert fits


def test_check_plan_spends_nothing(tmp_path):
    budget = fresh(tmp_path, cap=100)
    budget.check_plan(90, "a plan that is only considered")
    assert budget.spent() == 0


def test_invocations_are_recorded_for_the_audit_trail(tmp_path):
    budget = fresh(tmp_path)
    budget.charge(2, "work")
    budget.note("run k1", run_id="r1", calls=2)
    ledger = json.loads((tmp_path / "budget.json").read_text())
    assert ledger["spent"] == 2
    assert len(ledger["invocations"]) == 1
    assert ledger["invocations"][0]["label"] == "run k1"
    assert ledger["invocations"][0]["calls"] == 2
    assert "at" in ledger["invocations"][0]


def test_no_temporary_file_is_left_behind(tmp_path):
    budget = fresh(tmp_path)
    budget.charge(1, "work")
    budget.note("run", calls=1)
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "budget.json"]
    assert leftovers == []


def test_an_unreadable_ledger_stops_the_run_rather_than_resetting_it(tmp_path):
    path = tmp_path / "budget.json"
    path.write_text("{ this is not json")
    budget = CallBudget(path=path, cap=10)
    # Reading zero here would silently hand back the whole cap a second time.
    with pytest.raises(SystemExit):
        budget.spent()


def test_the_cap_is_the_one_the_caller_asked_for(tmp_path):
    assert fresh(tmp_path, cap=1500).remaining() == 1500
    assert "of 1500" in fresh(tmp_path, cap=1500).describe()


def test_the_k3_cap_is_the_one_the_protocol_freezes():
    """protocol_k3.md raises the hard cap to 6000 calls including retries."""
    from call_budget import HARD_CAP

    assert HARD_CAP == 6000


def test_the_default_ledger_carries_the_k3_cap(tmp_path):
    from call_budget import HARD_CAP, CallBudget

    budget = CallBudget(path=tmp_path / "budget.json")
    assert budget.cap == HARD_CAP
    assert budget.remaining() == 6000
