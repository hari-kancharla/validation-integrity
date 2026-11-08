"""Spending safety checks; every ledger is disposable and no provider is called."""

import json
import multiprocessing
import time
from pathlib import Path

import pytest

from call_budget import BudgetExhausted, CallBudget


def _charge_worker(args):
    path, cap = args

    class SlowStore(CallBudget):
        def _store(self, ledger):
            # Widen overlapping writes so lost updates are observable before the fix.
            time.sleep(0.01)
            super()._store(ledger)

    budget = SlowStore(Path(path), cap=cap)
    accepted = 0
    errors = []
    for _ in range(10):
        try:
            budget.charge()
            budget.note("accepted", calls=1)
            accepted += 1
        except BudgetExhausted:
            break
        except Exception as error:
            errors.append(type(error).__name__)
    return accepted, errors


def test_concurrent_processes_cannot_overspend_or_lose_charges(tmp_path):
    path = tmp_path / "budget.json"
    cap = 37
    with multiprocessing.get_context("spawn").Pool(8) as pool:
        results = pool.map(_charge_worker, [(str(path), cap)] * 8)
    assert all(not errors for _, errors in results), results
    assert sum(accepted for accepted, _ in results) == cap
    assert CallBudget(path, cap=cap).spent() == cap
    assert len(CallBudget(path, cap=cap).load()["invocations"]) == cap


@pytest.mark.parametrize("count", [-1, 0, True, 1.5, "1"])
def test_invalid_charge_sizes_cannot_reopen_the_budget(tmp_path, count):
    path = tmp_path / "budget.json"
    budget = CallBudget(path, cap=10)
    budget.charge(3)
    original = path.read_bytes()
    with pytest.raises(ValueError):
        budget.charge(count)
    assert path.read_bytes() == original


@pytest.mark.parametrize("planned", [-1, True, 1.5, "1"])
def test_invalid_plan_sizes_are_refused_without_writing(tmp_path, planned):
    path = tmp_path / "budget.json"
    with pytest.raises(ValueError):
        CallBudget(path, cap=10).check_plan(planned, "invalid")
    assert not path.exists()


@pytest.mark.parametrize(
    "ledger",
    [
        [],
        {},
        {"cap": 10, "spent": -1, "invocations": []},
        {"cap": 10, "spent": True, "invocations": []},
        {"cap": 10, "spent": "0", "invocations": []},
        {"cap": 10, "spent": 0, "invocations": {}},
    ],
)
def test_malformed_ledgers_fail_closed_without_rewriting(tmp_path, ledger):
    path = tmp_path / "budget.json"
    path.write_text(json.dumps(ledger))
    original = path.read_bytes()
    with pytest.raises(SystemExit):
        CallBudget(path, cap=10).charge()
    assert path.read_bytes() == original


def test_failed_storage_preserves_the_previous_ledger_and_refuses_charge(tmp_path, monkeypatch):
    import call_budget

    path = tmp_path / "budget.json"
    budget = CallBudget(path, cap=10)
    budget.charge(3)
    before = path.read_bytes()

    def failed_replace(*args):
        raise OSError("injected storage failure")

    monkeypatch.setattr(call_budget.os, "replace", failed_replace)
    with pytest.raises(OSError):
        budget.charge()
    assert path.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["budget.json"]


def test_duplicate_accounting_keys_are_refused(tmp_path):
    path = tmp_path / "budget.json"
    path.write_text('{"cap":10,"spent":7,"spent":0,"invocations":[]}')
    with pytest.raises(SystemExit):
        CallBudget(path, cap=10).charge()
