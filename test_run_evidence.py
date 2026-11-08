"""Resuming never reuses stale observations or loses failed planned cells."""

import copy
import json
from types import SimpleNamespace

import pytest

import recording
import run_evidence as evidence
import run_experiment


def setup(tmp_path):
    directory = tmp_path / "run"
    directory.mkdir()
    payload_root = tmp_path / "payloads"
    item = {
        "reviewer": "model-a",
        "case_id": "case-a",
        "variant": "a",
        "truth": "correct",
        "tier": "authored",
        "domain": "auth",
        "condition": "E_NONE",
        "sample_idx": 0,
    }
    payload = "Inspect this implementation.\n"
    path = payload_root / "case-a/a/E_NONE.md"
    path.parent.mkdir(parents=True)
    path.write_text(payload)
    plan = evidence.build_plan(
        blocks=[("model-a", [item, {**item, "sample_idx": 1}, {**item, "sample_idx": 2}])],
        mode="k3p",
        run_tier="P",
        seed=1337,
        smoke=False,
        reliance_probe=False,
        frozen_files={"protocol.md": "a" * 64},
        payload_reader=lambda _: payload,
        configuration={"model": "model-a"},
    )
    evidence.prepare_run(directory, plan)
    sample = SimpleNamespace(
        status="OK",
        response_raw='{"suspicion":0,"verdict":"APPROVE","reason":"checked"}',
        suspicion=0,
        verdict="APPROVE",
        reason="checked",
        response_tokens=3,
        latency_ms=1,
    )
    row = recording.build_record(
        item=item, payload=payload, sample=sample, run_tier="P", ts="2026-10-19T00:00:00Z"
    )
    return directory, payload_root, plan, row


def test_old_resume_silently_skipped_malformed_records(tmp_path):
    directory, _, _, row = setup(tmp_path)
    path = directory / "records.jsonl"
    path.write_text(json.dumps(row) + "\n{partial\n")
    before = path.read_bytes()
    with pytest.raises(ValueError):
        run_experiment.already_recorded(path)
    assert path.read_bytes() == before


def test_failed_records_are_retained_and_missing_cells_remain_visible(tmp_path):
    directory, payload_root, plan, row = setup(tmp_path)
    failed = {
        **row,
        "sample_idx": 1,
        "status": "TRANSPORT_FAIL",
        "suspicion": None,
        "verdict": None,
        "response_raw": None,
        "response_chars": 0,
    }
    (directory / "records.jsonl").write_text(json.dumps(row) + "\n" + json.dumps(failed) + "\n")
    report = evidence.audit_run(directory, payload_root)
    assert (
        report["planned_observations"],
        report["recorded"],
        report["ok"],
        report["transport_failed"],
        report["not_recorded"],
    ) == (3, 2, 1, 1, 1)
    assert len(run_experiment.already_recorded(directory / "records.jsonl", plan)) == 2
    assert [r["status"] for r in report["observations"]] == ["OK", "TRANSPORT_FAIL", "NOT_RECORDED"]


@pytest.mark.parametrize(
    "fault",
    ["duplicate", "unknown_status", "payload", "reviewer", "truth", "boolean_sample", "truncated"],
)
def test_invalid_records_cannot_count_as_completed(tmp_path, fault):
    directory, _, plan, row = setup(tmp_path)
    if fault == "unknown_status":
        row["status"] = "unknown"
    elif fault == "payload":
        row["payload_sha256"] = "b" * 64
    elif fault == "reviewer":
        row["reviewer"] = "different"
    elif fault == "truth":
        row["truth"] = "incorrect"
    elif fault == "boolean_sample":
        row["sample_idx"] = False
    body = json.dumps(row) + "\n"
    if fault == "duplicate":
        body += body
    if fault == "truncated":
        body += "{partial"
    path = directory / "records.jsonl"
    path.write_text(body)
    before = path.read_bytes()
    with pytest.raises(ValueError):
        evidence.validate_records(path, plan)
    assert path.read_bytes() == before


@pytest.mark.parametrize("field", ["mode", "seed", "reliance_probe", "configuration"])
def test_changed_resume_plan_is_refused_without_writes(tmp_path, field):
    directory, _, plan, _ = setup(tmp_path)
    changed = copy.deepcopy(plan)
    changed[field] = "different"
    before = (directory / "plan.json").read_bytes()
    with pytest.raises(ValueError, match="changed"):
        evidence.prepare_run(directory, changed)
    assert (directory / "plan.json").read_bytes() == before


def test_payload_drift_and_legacy_unbound_runs_are_refused(tmp_path):
    directory, payload_root, plan, row = setup(tmp_path)
    (payload_root / "case-a/a/E_NONE.md").write_text("changed")
    with pytest.raises(ValueError, match="payload"):
        evidence.audit_run(directory, payload_root)
    (directory / "records.jsonl").write_text(json.dumps(row) + "\n")
    (directory / "plan.json").unlink()
    with pytest.raises(ValueError, match="no frozen"):
        evidence.prepare_run(directory, plan)


def test_single_writer_lock_prevents_duplicate_collection(tmp_path):
    with evidence.collection_lock(tmp_path):
        with pytest.raises(ValueError, match="another process"):
            with evidence.collection_lock(tmp_path):
                pass


def test_uncertain_attempt_blocks_resume_without_inventing_an_observation(tmp_path):
    directory, _, plan, row = setup(tmp_path)
    evidence.mark_attempt(directory, plan, plan["items"][0])
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    with pytest.raises(ValueError, match="uncertain"):
        evidence.prepare_run(directory, plan)
    assert {p.name: p.read_bytes() for p in directory.iterdir()} == before
    (directory / "records.jsonl").write_text(json.dumps(row) + "\n")
    assert len(evidence.prepare_run(directory, plan)) == 1
    assert not (directory / "inflight.json").exists()


def test_resume_does_not_call_recorded_cells_or_erase_session_history(tmp_path, monkeypatch):
    from call_budget import CallBudget

    directory, payload_root, plan, row = setup(tmp_path)
    (directory / "records.jsonl").write_text(json.dumps(row) + "\n")
    calls = []

    class Client:
        def __init__(self, model, budget=None):
            self.budget = budget
            self.calls_made = 0

        def review(self, payload):
            self.budget.charge()
            self.calls_made += 1
            calls.append(payload)
            return SimpleNamespace(
                status="OK",
                response_raw='{"suspicion":0,"verdict":"APPROVE","reason":"checked"}',
                suspicion=0,
                verdict="APPROVE",
                reason="checked",
                response_tokens=3,
                latency_ms=1,
            )

        def describe(self):
            return {"provider": "fixture"}

    monkeypatch.setattr(run_experiment, "ReviewerClient", Client)
    monkeypatch.setattr(
        run_experiment,
        "payload_path",
        lambda item: payload_root / item["case_id"] / item["variant"] / f"{item['condition']}.md",
    )
    args = SimpleNamespace(mode="k3p", reliance_probe=False, smoke=False)
    blocks = [("model-a", plan["items"])]
    budget = CallBudget(tmp_path / "budget.json", cap=10)
    parameters = (
        args,
        directory,
        plan,
        blocks,
        budget,
        ["model-a"],
        [{"case_id": "case-a"}],
        ("E_NONE",),
        "P",
        3,
        [],
    )
    with evidence.collection_lock(directory):
        assert run_experiment._collect_run(*parameters) == 0
    manifest = json.loads((directory / "manifest.json").read_text())
    started = manifest["started_at"]
    assert len(calls) == 2 and budget.spent() == 2
    with evidence.collection_lock(directory):
        assert run_experiment._collect_run(*parameters) == 0
    manifest = json.loads((directory / "manifest.json").read_text())
    assert len(calls) == 2 and budget.spent() == 2 and manifest["records_written"] == 3
    assert manifest["started_at"] == started and len(manifest["sessions"]) == 2


def test_changed_payload_stops_before_client_call(tmp_path, monkeypatch):
    from call_budget import CallBudget

    directory, payload_root, plan, _ = setup(tmp_path)
    path = payload_root / "case-a/a/E_NONE.md"
    path.write_text("changed")

    class Client:
        calls_made = 0

        def __init__(self, **kwargs):
            pass

        def review(self, *args):
            raise AssertionError("drifted payload must never be sent")

    monkeypatch.setattr(run_experiment, "ReviewerClient", Client)
    monkeypatch.setattr(run_experiment, "payload_path", lambda item: path)
    args = SimpleNamespace(mode="k3p", reliance_probe=False, smoke=False)
    with pytest.raises(ValueError, match="payload changed"):
        run_experiment._collect_run(
            args,
            directory,
            plan,
            [("model-a", plan["items"])],
            CallBudget(tmp_path / "budget.json"),
            ["model-a"],
            [],
            ("E_NONE",),
            "P",
            3,
            [],
        )
    assert not (tmp_path / "budget.json").exists()


def test_protocol_permitted_schema_repair_is_not_reclassified(tmp_path, monkeypatch):
    from reviewer_client import ReviewerClient

    directory, _, plan, _ = setup(tmp_path)
    client = ReviewerClient(model="fixture")
    replies = iter(
        [
            '{"wrong":true}',
            'Preamble\n---\n{"suspicion":0,"verdict":"APPROVE","reason":""}\n---\nend',
        ]
    )
    monkeypatch.setattr(client, "_send", lambda *args, **kwargs: next(replies))
    sample = client.review("Inspect this implementation.\n")
    assert sample.status == "OK" and sample.reason == ""
    row = recording.build_record(
        item=plan["items"][0],
        payload="Inspect this implementation.\n",
        sample=sample,
        run_tier="P",
        ts="2026-10-19T00:00:00Z",
    )
    path = directory / "records.jsonl"
    path.write_text(json.dumps(row) + "\n")
    assert evidence.validate_records(path, plan) == [row]


@pytest.mark.parametrize("status", ["INVALID", "TRANSPORT_FAIL"])
def test_parseable_success_cannot_be_relabelled_as_failure(tmp_path, status):
    directory, _, plan, row = setup(tmp_path)
    row.update(status=status, suspicion=None, verdict=None)
    path = directory / "records.jsonl"
    path.write_text(json.dumps(row) + "\n")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="successful first response"):
        evidence.validate_records(path, plan)
    assert path.read_bytes() == before


def test_failed_manifest_replacement_preserves_history(tmp_path, monkeypatch):
    path = tmp_path / "manifest.json"
    original = {"started_at": "first", "sessions": [{"http_calls": 2}]}
    evidence.write_document(path, original)
    before = path.read_bytes()

    def fail(*args):
        raise OSError("simulated manifest replacement failure")

    monkeypatch.setattr(evidence.os, "replace", fail)
    with pytest.raises(OSError, match="replacement"):
        evidence.write_document(path, {**original, "sessions": []})
    assert path.read_bytes() == before
    assert [p.name for p in tmp_path.iterdir()] == [path.name]


def test_broken_manifest_symlink_stops_before_collection(tmp_path):
    from call_budget import CallBudget

    directory, _, plan, _ = setup(tmp_path)
    (directory / "manifest.json").symlink_to(tmp_path / "absent.json")
    args = SimpleNamespace(mode="k3p", reliance_probe=False, smoke=False)
    with pytest.raises(ValueError, match="symlink"):
        run_experiment._collect_run(
            args,
            directory,
            plan,
            [("model-a", plan["items"])],
            CallBudget(tmp_path / "budget.json"),
            ["model-a"],
            [],
            ("E_NONE",),
            "P",
            3,
            [],
        )
    assert not (tmp_path / "budget.json").exists()
