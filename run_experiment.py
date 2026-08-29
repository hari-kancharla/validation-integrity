#!/usr/bin/env python3
"""Run K1 and K2: build, gate, plan, and — only on explicit confirmation — collect samples.

Default behaviour is a dry run. No reviewer call is made unless ``CONFIRM_RUN=1``; a dry run
prints the plan and stops without creating a run directory, because a dry run produces no
results.

Two modes:

``--mode k1``
    The original pilot: the adapted cases only, the three K1 conditions, one reviewer.
    7 x 2 x 3 x 3 = 126 calls.

``--mode k2``
    The full grid: every case, all five conditions, one reviewer at a time.
    13 x 2 x 5 x 3 = 390 calls per reviewer, less any cell with no independent suite.

``--mode k3p``
    K3 Tier P, power. Every case in the pool, both variants, ``E_NONE`` and ``E_COUPLED``
    only, 3 samples, one reviewer at a time. This tier carries the primary hypothesis at
    full n and nothing else.

``--mode k3m``
    K3 Tier M, mechanism. The 30 cases frozen in ``mechanism_subset.json``, all seven
    conditions, 3 samples. ``--reliance-probe`` adds one further call per unit, on
    ``sample_idx`` 0 only, asking the reviewer what it relied on.

The two K3 tiers are separate runs on purpose, so spending can be staged: Tier P can be
collected, read and paid for before Tier M is authorised, and either can be re-run alone.

Ordering inside a reviewer's block is fixed by ``random.Random(1337)`` and is the same for
every reviewer, so order effects are held constant across the matrix. Records are appended
one JSON line per sample and a re-run against an existing run directory skips the tuples
already recorded, so an interrupted run resumes rather than duplicating work.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import build_payloads
import mechanism_subset
import recording
from call_budget import HARD_CAP as HARD_CALL_CAP
from call_budget import BudgetExhausted, CallBudget
from reviewer_client import (
    STATUS_INVALID,
    STATUS_OK,
    STATUS_TRANSPORT_FAIL,
    ReviewerClient,
    resolve_model,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
CASES_DIR = HERE / "cases"
PAYLOADS_DIR = HERE / "payloads"
RUNS_DIR = HERE / "runs"

SEED = 1337
SAMPLES_PER_CELL = 3
VARIANTS = ("a", "b")
BRANCH = "A"

CONDITIONS_K1 = ("E_NONE", "E_COUPLED", "E_LABELSWAP")
CONDITIONS_K2 = ("E_NONE", "E_COUPLED", "E_LABELSWAP", "E_INDEP", "E_INDEP_MISLABELED")
CONDITIONS_K3P = ("E_NONE", "E_COUPLED")
CONDITIONS_K3M = CONDITIONS_K2 + ("E_DOSE_LOW", "E_DOSE_HIGH")

CONDITIONS_BY_MODE = {
    "k1": CONDITIONS_K1,
    "k2": CONDITIONS_K2,
    "k3p": CONDITIONS_K3P,
    "k3m": CONDITIONS_K3M,
}
RUN_TIER_BY_MODE = {"k1": "P", "k2": "M", "k3p": "P", "k3m": "M"}

#: The probe is permitted in the mechanism tier only, and only on the first sample of a unit.
PROBE_MODES = ("k3m",)
PROBE_SAMPLE_INDEX = 0

# The cap itself lives in call_budget.py, where it is enforced across invocations.

PRICES_PER_MTOK = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-opus-5": (5.00, 25.00),
}

CHARS_PER_TOKEN = 4.0


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        return result.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 - recorded as unknown, never fatal
        return "unknown"


def run_gate(name: str) -> None:
    print(f"\n--- {name} ---")
    sys.stdout.flush()
    result = subprocess.run([sys.executable, str(HERE / name)], cwd=str(HERE))
    if result.returncode != 0:
        raise SystemExit(f"{name} failed with exit code {result.returncode}; refusing to run")


def load_cases(mode: str) -> list[dict]:
    cases = []
    subset = set(mechanism_subset.load_subset()) if mode == "k3m" else None
    for case_dir in sorted(p for p in CASES_DIR.iterdir() if p.is_dir()):
        meta = json.loads((case_dir / "meta.json").read_text())
        if mode == "k1" and meta.get("family") != "adapted":
            continue
        if subset is not None and case_dir.name not in subset:
            continue
        cases.append(
            {
                "case_id": case_dir.name,
                "correct_variant": meta["correct_variant"],
                "family": meta.get("family", "adapted"),
                "tier": meta.get("tier", "authored"),
                "domain": meta.get("domain", "unclassified"),
            }
        )
    if subset is not None and len(cases) != len(subset):
        missing = sorted(subset - {case["case_id"] for case in cases})
        raise SystemExit(
            f"the frozen mechanism subset names {len(missing)} case(s) the pool does not "
            f"hold: {missing[:5]}"
        )
    return cases


def resolve_reviewers(mode: str) -> list[str]:
    if mode == "k1":
        return [resolve_model()]
    raw = os.environ.get("REVIEWER_MODELS", "").strip()
    if not raw:
        return [resolve_model()]
    models = [item.strip() for item in raw.split(",") if item.strip()]
    if not models:
        raise SystemExit("REVIEWER_MODELS is set but lists no model")
    return models


def payload_path(item: dict) -> Path:
    return PAYLOADS_DIR / item["case_id"] / item["variant"] / f"{item['condition']}.md"


def build_reviewer_plan(cases: list[dict], conditions: tuple[str, ...], reviewer: str,
                        samples: int) -> tuple[list[dict], list[str]]:
    plan: list[dict] = []
    excluded: list[str] = []
    for case in cases:
        for variant in VARIANTS:
            truth = "correct" if variant == case["correct_variant"] else "incorrect"
            for condition in conditions:
                probe = {"case_id": case["case_id"], "variant": variant, "condition": condition}
                if not payload_path(probe).is_file():
                    excluded.append(f"{case['case_id']}|{variant}|{condition}")
                    continue
                for sample_idx in range(samples):
                    plan.append(
                        {
                            "reviewer": reviewer,
                            "case_id": case["case_id"],
                            "variant": variant,
                            "truth": truth,
                            "tier": case.get("tier", "authored"),
                            "domain": case.get("domain", "unclassified"),
                            "condition": condition,
                            "sample_idx": sample_idx,
                        }
                    )
    # Same seed for every reviewer, so each sees the grid in the same order.
    random.Random(SEED).shuffle(plan)
    return plan, excluded


def tier_table(reviewers: list[str], samples: int) -> str:
    """Call count and cost for every tier and every reviewer, whichever tier is being run.

    Printed whole so the money gate shows what the rest of the design would cost before
    any of it is authorised, not just the slice about to run.
    """
    lines = [
        f"  {'tier':6s} {'reviewer':28s} {'cases':>5s} {'calls':>6s} {'probe':>6s} "
        f"{'total':>6s} {'input tok':>11s} {'cost':>9s}"
    ]
    grand = 0
    for mode in ("k3p", "k3m"):
        cases = load_cases(mode)
        conditions = CONDITIONS_BY_MODE[mode]
        for reviewer in reviewers:
            plan, _excluded = build_reviewer_plan(cases, conditions, reviewer, samples)
            probe = (
                len([item for item in plan if item["sample_idx"] == PROBE_SAMPLE_INDEX])
                if mode in PROBE_MODES
                else 0
            )
            cost, input_tokens, _out = estimate(plan, reviewer)
            probe_cost, probe_tokens, _po = estimate(
                [i for i in plan if i["sample_idx"] == PROBE_SAMPLE_INDEX], reviewer
            ) if probe else (0.0, 0, 0)
            total_cost = None if cost is None else cost + (probe_cost or 0.0)
            if total_cost is not None:
                grand += total_cost
            rendered = "unknown" if total_cost is None else f"${total_cost:.2f}"
            lines.append(
                f"  {mode:6s} {reviewer:28s} {len(cases):5d} {len(plan):6d} {probe:6d} "
                f"{len(plan) + probe:6d} {input_tokens + probe_tokens:11,d} {rendered:>9s}"
            )
        grand_calls = None
    lines.append(f"  {'':6s} {'':28s} {'':5s} {'':6s} {'':6s} {'':6s} {'':11s} "
                 f"<= ${grand:.2f}")
    lines.append("  The probe column is the mechanism tier's second call per unit, which is")
    lines.append("  collected only when --reliance-probe is passed.")
    return "\n".join(lines)


def estimate(plan: list[dict], model: str) -> tuple[float | None, int, int]:
    input_tokens = sum(
        math.ceil(len(payload_path(item).read_text()) / CHARS_PER_TOKEN) for item in plan
    )
    output_tokens = len(plan) * 600
    prices = PRICES_PER_MTOK.get(model)
    if prices is None:
        return None, input_tokens, output_tokens
    return input_tokens / 1e6 * prices[0] + output_tokens / 1e6 * prices[1], input_tokens, output_tokens


def key_of(item: dict) -> tuple:
    return (
        item.get("reviewer"),
        item["case_id"],
        item["variant"],
        item["condition"],
        item["sample_idx"],
    )


def already_recorded(records_path: Path) -> set[tuple]:
    done: set[tuple] = set()
    if not records_path.is_file():
        return done
    for line in records_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            done.add(key_of(json.loads(line)))
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the K1 pilot or the K2 grid.")
    parser.add_argument("--mode", choices=("k1", "k2", "k3p", "k3m"), default="k1")
    parser.add_argument("--reliance-probe", action="store_true",
                        help="mechanism tier only: one further call per unit, on the first "
                             "sample, asking the reviewer what it relied on")
    parser.add_argument("--run-dir", default=os.environ.get("K1_RUN_DIR"))
    parser.add_argument("--smoke", action="store_true",
                        help="Bounded transport check: the first case only, one sample per "
                             "cell. Writes to runs/smoke_<stamp>/, which analyze.py ignores.")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    conditions = CONDITIONS_BY_MODE[args.mode]
    run_tier = RUN_TIER_BY_MODE[args.mode]
    if args.reliance_probe and args.mode not in PROBE_MODES:
        raise SystemExit(
            f"--reliance-probe is permitted in {', '.join(PROBE_MODES)} only; "
            f"protocol_k3.md confines it to the mechanism tier"
        )
    print(f"{args.mode} run (tier {run_tier})")
    print(f"  branch: {BRANCH}")
    print(f"  repository commit: {git_commit()}")

    if args.skip_build:
        print("\n--- build_payloads (skipped by request) ---")
    else:
        print("\n--- build_payloads ---")
        sys.stdout.flush()
        build_payloads.build_payloads(build_payloads.materialize_cases())
    run_gate("lint_cases.py")
    run_gate("lint_payloads.py")
    run_gate("lint_payloads_k2.py")
    if args.mode.startswith("k3"):
        run_gate("lint_payloads_k3.py")

    cases = load_cases(args.mode)
    reviewers = resolve_reviewers(args.mode)
    samples = 1 if args.smoke else SAMPLES_PER_CELL
    if args.smoke:
        keep = sorted(case["case_id"] for case in cases)[0]
        cases = [case for case in cases if case["case_id"] == keep]
        print(f"\n  SMOKE MODE: {keep} only, one sample per cell")

    blocks = []
    total_calls = 0
    probe_calls = 0
    all_excluded: list[str] = []
    for reviewer in reviewers:
        plan, excluded = build_reviewer_plan(cases, conditions, reviewer, samples)
        blocks.append((reviewer, plan))
        total_calls += len(plan)
        if args.reliance_probe:
            probe_calls += sum(
                1 for item in plan if item["sample_idx"] == PROBE_SAMPLE_INDEX
            )
        all_excluded = excluded
    # The probe is a real call against the same ledger, so the gate has to count it.
    total_calls += probe_calls

    print("\n--- every tier, per reviewer, at today's pool ---")
    print(tier_table(reviewers, samples))

    print("\n--- plan ---")
    print(f"  mode:             {args.mode}{' (SMOKE)' if args.smoke else ''}")
    print(f"  cases:            {len(cases)}")
    print(f"  conditions:       {len(conditions)} ({', '.join(conditions)})")
    print(f"  samples/cell:     {samples}")
    print(f"  reviewers:        {len(reviewers)} ({', '.join(reviewers)})")
    available = sorted({
        item["condition"] for _reviewer, plan in blocks for item in plan
    })
    missing = [c for c in conditions if c not in available]
    if missing:
        print(f"  conditions with no payload anywhere: {', '.join(missing)}")
        print(f"                    the remaining {len(available)} will be collected; the "
              f"cell-exclusion rule in protocol_k2.md covers this")
    if args.reliance_probe:
        print(f"  reliance probe:   on, {probe_calls} further call(s) "
              f"(sample #{PROBE_SAMPLE_INDEX} of each unit)")
    if all_excluded:
        print(f"  excluded cells:   {len(all_excluded)} with no payload")
        for item in all_excluded[:6]:
            print(f"                    {item}")
        if len(all_excluded) > 6:
            print(f"                    ... and {len(all_excluded) - 6} more")
    grand_cost = 0.0
    unknown_price = False
    for reviewer, plan in blocks:
        cost, input_tokens, _output = estimate(plan, reviewer)
        if cost is None:
            unknown_price = True
            print(f"  [{reviewer}] {len(plan)} calls, ~{input_tokens:,} input tokens, "
                  f"cost unknown (no list price on file)")
        else:
            grand_cost += cost
            print(f"  [{reviewer}] {len(plan)} review calls, ~{input_tokens:,} input "
                  f"tokens, <= ${cost:.2f} at list prices")
        if args.reliance_probe:
            probes = [i for i in plan if i["sample_idx"] == PROBE_SAMPLE_INDEX]
            probe_cost, probe_tokens, _out = estimate(probes, reviewer)
            if probe_cost is not None:
                grand_cost += probe_cost
            print(f"  [{reviewer}] {len(probes)} probe calls, ~{probe_tokens:,} input "
                  f"tokens, "
                  f"{'cost unknown' if probe_cost is None else f'<= ${probe_cost:.2f}'}")
    budget = CallBudget()
    fits, ledger_message = budget.check_plan(total_calls, f"mode {args.mode}")
    print(f"  PLANNED CALLS:    {total_calls}")
    print(f"  call ledger:      {budget.describe()}")
    print(f"  ledger check:     {ledger_message}")
    print(f"  ESTIMATED COST:   "
          f"{'>= ' if unknown_price else '<= '}${grand_cost:.2f}, upper bound at list prices")
    print(f"  order seed:       {SEED}")

    if not fits:
        print(f"\nSTOP: {ledger_message}.")
        print("Nothing was spent. Reduce the plan, or inspect the ledger with")
        print("  python call_budget.py")
        return 2

    if os.environ.get("CONFIRM_RUN") != "1":
        print("\n=== MONEY GATE ===")
        print("CONFIRM_RUN is not 1, so this was a dry run. No reviewer call was made and")
        print("no run directory was created. To execute the plan above, re-run with")
        print("CONFIRM_RUN=1 in the environment.")
        return 0

    prefix = "smoke_" if args.smoke else f"{args.mode}_"
    run_dir = Path(args.run_dir) if args.run_dir else RUNS_DIR / f"{prefix}{utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    records_path = run_dir / "records.jsonl"
    manifest_path = run_dir / "manifest.json"
    done = already_recorded(records_path)

    started_at = datetime.now(timezone.utc).isoformat()
    stopped_early = None
    calls_made = 0
    per_reviewer: dict[str, dict] = {}

    for reviewer, plan in blocks:
        remaining = [item for item in plan if key_of(item) not in done]
        cost, _input_tokens, _output = estimate(remaining, reviewer)
        print(f"\n=== reviewer {reviewer} ===")
        print(f"  already recorded: {len(plan) - len(remaining)}")
        print(f"  to collect now:   {len(remaining)}")
        print(f"  cost for this reviewer: "
              f"{'unknown' if cost is None else f'<= ${cost:.2f}'}")
        sys.stdout.flush()
        if not remaining:
            continue

        client = ReviewerClient(model=reviewer, budget=budget)
        with records_path.open("a") as handle:
            for index, item in enumerate(remaining, start=1):
                payload = payload_path(item).read_text()
                try:
                    sample = client.review(payload)
                except BudgetExhausted as exhausted:
                    stopped_early = str(exhausted)
                    print(f"  STOP: {stopped_early}")
                    break
                reliance = None
                if (
                    args.reliance_probe
                    and item["sample_idx"] == PROBE_SAMPLE_INDEX
                    and sample.status == STATUS_OK
                    and sample.response_raw
                ):
                    try:
                        reliance = client.probe_reliance(payload, sample.response_raw)
                    except BudgetExhausted as exhausted:
                        stopped_early = str(exhausted)
                        print(f"  STOP: {stopped_early}")
                record = recording.build_record(
                    item=item,
                    payload=payload,
                    sample=sample,
                    run_tier=run_tier,
                    ts=datetime.now(timezone.utc).isoformat(),
                    reliance=reliance,
                )
                handle.write(json.dumps(record) + "\n")
                handle.flush()
                marker = {STATUS_OK: ".", STATUS_INVALID: "I", STATUS_TRANSPORT_FAIL: "T"}[
                    sample.status
                ]
                probe_marker = "" if reliance is None else f" +probe:{reliance['status']}"
                print(f"  [{index}/{len(remaining)}] {marker} {item['case_id']} "
                      f"{item['variant']} {item['condition']} #{item['sample_idx']} "
                      f"({sample.latency_ms} ms){probe_marker}")
                if stopped_early:
                    break
        calls_made += client.calls_made
        per_reviewer[reviewer] = {"planned": len(plan), "http_calls": client.calls_made}
        budget.note(
            f"run {args.mode} / {reviewer}",
            run_id=run_dir.name,
            calls=client.calls_made,
        )
        if stopped_early:
            break

    totals = {"OK": 0, STATUS_INVALID: 0, STATUS_TRANSPORT_FAIL: 0}
    for line in records_path.read_text().splitlines():
        if not line.strip():
            continue
        status = json.loads(line).get("status", "OK")
        totals[status if status in totals else "OK"] += 1

    manifest = {
        "run_id": run_dir.name,
        "mode": args.mode,
        "run_tier": run_tier,
        "reliance_probe": bool(args.reliance_probe),
        "mechanism_subset_sha256": (
            json.loads((HERE / "mechanism_subset.json").read_text()).get("pool_sha256")
            if args.mode == "k3m" and (HERE / "mechanism_subset.json").is_file()
            else None
        ),
        "smoke": bool(args.smoke),
        "git_commit": git_commit(),
        "provider": ReviewerClient(model=reviewers[0]).describe()["provider"],
        "model": reviewers[0],
        "reviewers": reviewers,
        "temperature": 0.7,
        "max_tokens": 600,
        "seed": SEED,
        "planned_calls": total_calls,
        "branch": BRANCH,
        "cases": [case["case_id"] for case in cases],
        "case_tiers": {case["case_id"]: case.get("tier", "authored") for case in cases},
        "case_domains": {case["case_id"]: case.get("domain", "unclassified") for case in cases},
        "conditions": list(conditions),
        "samples_per_cell": samples,
        "excluded_cells": all_excluded,
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "invalid_count": totals[STATUS_INVALID],
        "transport_fail_count": totals[STATUS_TRANSPORT_FAIL],
        "records_written": sum(totals.values()),
        "http_calls_this_session": calls_made,
        "per_reviewer": per_reviewer,
        "hard_call_cap": HARD_CALL_CAP,
        "budget_spent_after": budget.spent(),
        "stopped_early": stopped_early,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print("\n--- run summary ---")
    print(f"  records:        {manifest['records_written']} / {total_calls} planned")
    print(f"  invalid:        {manifest['invalid_count']}")
    print(f"  transport fail: {manifest['transport_fail_count']}")
    print(f"  http calls:     {calls_made}")
    print(f"  call ledger:    {budget.describe()}")
    print(f"  manifest:       {manifest_path.relative_to(HERE)}")
    return 0 if stopped_early is None else 3


if __name__ == "__main__":
    raise SystemExit(main())
