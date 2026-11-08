"""Frozen call-plan bindings and read-only coverage for study execution records."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

import recording
from reviewer_client import STATUS_INVALID, STATUS_OK, STATUS_TRANSPORT_FAIL, parse_review

MAX_BYTES = 64 * 1024 * 1024
STATUSES = {STATUS_OK, STATUS_INVALID, STATUS_TRANSPORT_FAIL}
KEY_FIELDS = ("reviewer", "case_id", "variant", "condition", "sample_idx")


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field in study evidence")
        result[key] = value
    return result


def _float(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite study evidence")
    return parsed


def _constant(value):
    raise ValueError("non-finite study evidence")


def loads(body):
    try:
        return json.loads(
            body, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float
        )
    except RecursionError as error:
        raise ValueError("study evidence nesting is too deep") from error


def read(path):
    if path.is_symlink():
        raise ValueError("study evidence cannot be a symlink")
    with path.open("rb") as stream:
        body = stream.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError("study evidence exceeds the byte limit")
    return body.decode("utf-8")


def write_document(path, value):
    """Replace a durable document without truncating its previous version."""
    if path.is_symlink():
        raise ValueError("study evidence cannot be a symlink")
    body = json.dumps(value, indent=2, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".evidence-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def key(item):
    return tuple(item[field] for field in KEY_FIELDS)


def build_plan(
    *,
    blocks,
    mode,
    run_tier,
    seed,
    smoke,
    reliance_probe,
    frozen_files,
    payload_reader,
    configuration,
):
    items = []
    for reviewer, block in blocks:
        for item in block:
            payload = payload_reader(item)
            items.append(
                {
                    **item,
                    "payload_sha256": recording.payload_digest(payload),
                    "payload_chars": len(payload),
                    "tests_shown": recording.count_tests_shown(payload),
                }
            )
    if not items or len({key(item) for item in items}) != len(items):
        raise ValueError("call plan contains duplicate reviewer cells")
    return {
        "samples_per_cell": max(item["sample_idx"] for item in items) + 1,
        "schema": "validation-integrity.call-plan/1",
        "mode": mode,
        "run_tier": run_tier,
        "seed": seed,
        "smoke": smoke,
        "reliance_probe": reliance_probe,
        "frozen_files": frozen_files,
        "configuration": configuration,
        "items": items,
    }


def read_plan(directory):
    saved = loads(read(directory / "plan.json"))
    if not isinstance(saved, dict) or saved.get("sha256") != digest(saved.get("plan")):
        raise ValueError("study call-plan digest mismatch")
    plan = saved["plan"]
    if (
        not isinstance(plan, dict)
        or plan.get("schema") != "validation-integrity.call-plan/1"
        or not isinstance(plan.get("items"), list)
        or not plan["items"]
    ):
        raise ValueError("unsupported study call plan")
    for item in plan["items"]:
        if (
            not isinstance(item, dict)
            or type(item.get("sample_idx")) is not int
            or item["sample_idx"] < 0
        ):
            raise ValueError("invalid planned study cell")
        if not isinstance(item.get("case_id"), str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]*", item["case_id"]
        ):
            raise ValueError("invalid study case id")
        if (
            item.get("variant") not in {"a", "b"}
            or not isinstance(item.get("condition"), str)
            or not re.fullmatch(r"E_[A-Z_]+", item["condition"])
        ):
            raise ValueError("invalid study payload location")
    if len({key(item) for item in plan["items"]}) != len(plan["items"]):
        raise ValueError("duplicate planned study cells")
    return plan


def response_matches(raw, expected):
    """Replay the unchanged client's first-response/one-repair parsing contract."""
    first = parse_review(raw)
    if first is not None:
        return first == expected
    separator = "\n---\n"
    start = 0
    while True:
        boundary = raw.find(separator, start)
        if boundary < 0:
            return False
        if (
            parse_review(raw[:boundary]) is None
            and parse_review(raw[boundary + len(separator) :]) == expected
        ):
            return True
        start = boundary + len(separator)


def validate_records(path, plan):
    if not path.exists() and not path.is_symlink():
        return []
    rows = []
    seen = set()
    expected = {key(item): item for item in plan["items"]}
    for number, line in enumerate(read(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = loads(line)
            if not isinstance(row, dict) or set(row) != set(recording.RECORD_FIELDS):
                raise ValueError("record does not match the frozen observation schema")
            identity = key(row)
            if identity in seen or identity not in expected:
                raise ValueError("duplicate or unplanned observation")
            item = expected[identity]
            for field, value in item.items():
                if field not in row or type(row[field]) is not type(value) or row[field] != value:
                    raise ValueError(f"observation differs from its plan: {field}")
            if row["run_tier"] != plan["run_tier"] or row["status"] not in STATUSES:
                raise ValueError("unknown observation status or tier")
            raw = row["response_raw"]
            if raw is not None and not isinstance(raw, str):
                raise ValueError("response must be text or null")
            if row["response_chars"] != (len(raw) if raw is not None else 0):
                raise ValueError("response length mismatch")
            if row["status"] == STATUS_OK and (
                not isinstance(raw, str)
                or not response_matches(raw, (row["suspicion"], row["verdict"], row["reason"]))
            ):
                raise ValueError("successful observation differs from its captured response")
            if row["status"] != STATUS_OK and (
                row["suspicion"] is not None or row["verdict"] is not None
            ):
                raise ValueError("failed observation cannot carry a successful verdict")
            if row["status"] != STATUS_OK and raw is not None and parse_review(raw) is not None:
                raise ValueError("failed observation contains a successful first response")
            if identity != key(plan["items"][len(rows)]):
                raise ValueError("record order differs from the frozen call schedule")
            seen.add(identity)
            rows.append(row)
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"invalid study record at line {number}: {error}") from error
    return rows


def inspect_run(directory, expected_plan=None):
    if (directory / "plan.json").is_symlink():
        raise ValueError("study call plan cannot be a symlink")
    if not (directory / "plan.json").exists():
        if (directory / "records.jsonl").exists():
            raise ValueError("existing records have no frozen call plan; refusing unsafe resume")
        if directory.exists() and any(directory.iterdir()):
            raise ValueError("existing run directory has unbound files")
        return []
    plan = read_plan(directory)
    if expected_plan is not None and plan != expected_plan:
        raise ValueError("resume plan or payload changed; use a separate run directory")
    rows = validate_records(directory / "records.jsonl", plan)
    marker = directory / "inflight.json"
    if marker.exists() or marker.is_symlink():
        active = loads(read(marker))
        if not isinstance(active, dict) or active.get("plan_sha256") != digest(plan):
            raise ValueError("in-flight attempt differs from the call plan")
        if tuple(active.get("key", [])) not in {key(row) for row in rows}:
            raise ValueError("uncertain in-flight attempt; inspect its evidence before resuming")
    return rows


def prepare_run(directory, plan):
    rows = inspect_run(directory, plan)
    path = directory / "plan.json"
    if not path.exists():
        write_document(path, {"plan": plan, "sha256": digest(plan)})
    if (directory / "inflight.json").exists():
        (directory / "inflight.json").unlink()
    return rows


@contextmanager
def collection_lock(directory):
    import fcntl

    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("another process is collecting into this run directory") from error
        yield
    finally:
        os.close(descriptor)


def audit_run(directory, payload_root):
    plan = read_plan(directory)
    for item in plan["items"]:
        path = payload_root / item["case_id"] / item["variant"] / f"{item['condition']}.md"
        if recording.payload_digest(read(path)) != item["payload_sha256"]:
            raise ValueError("current payload differs from the frozen call plan")
    rows = validate_records(directory / "records.jsonl", plan)
    by_key = {key(row): row for row in rows}
    population = [
        {
            **{field: item[field] for field in KEY_FIELDS},
            "status": by_key[key(item)]["status"] if key(item) in by_key else "NOT_RECORDED",
        }
        for item in plan["items"]
    ]
    return {
        "schema": "validation-integrity.run-coverage/1",
        "planned_observations": len(population),
        "recorded": len(rows),
        "ok": sum(row["status"] == STATUS_OK for row in rows),
        "invalid": sum(row["status"] == STATUS_INVALID for row in rows),
        "transport_failed": sum(row["status"] == STATUS_TRANSPORT_FAIL for row in rows),
        "not_recorded": len(population) - len(rows),
        "observations": population,
        "execution_performed": False,
    }


def mark_attempt(directory, plan, item):
    marker = directory / "inflight.json"
    if marker.exists() or marker.is_symlink():
        raise ValueError("an unresolved attempt already exists")
    body = json.dumps({"plan_sha256": digest(plan), "key": list(key(item))})
    with marker.open("x") as stream:
        stream.write(body + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        report = audit_run(args.directory, Path(__file__).resolve().parent / "payloads")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(
            json.dumps(
                {"status": "invalid_evidence", "error": str(error), "execution_performed": False}
            )
        )
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
