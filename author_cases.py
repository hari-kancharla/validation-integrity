#!/usr/bin/env python3
"""Materialize the authored twin pool from compact specs, then prove every one of them.

A twin is written once, as a correct implementation plus the exact edits that produce its
incorrect sibling. Writing the sibling as an edit rather than as a second copy is what keeps
the planted defect a single, reviewable change instead of a diff that drifts, and it makes a
silent divergence between the two variants impossible: an edit whose target is not found is
an error, not a no-op.

Each spec yields, under ``authored/<case_id>/``:

    contract.md                  the specification both variants target
    case.json                    domain and tier, carried into meta.json by build_payloads
    correct/app/<module>.py      the implementation that satisfies the contract
    correct/tests/<test>.py      the visible suite, green on the correct implementation
    correct/reserve/<more>.py    further green tests, shown only by E_DOSE_HIGH
    incorrect/...                the same three files with the spec's edits applied
    oracle/<contract test>.py    the trusted checks, green on correct and red on incorrect

Everything is then verified by execution before ``lint_cases.py`` ever sees it: each visible
suite is green on its own variant, each reserve is green on its own variant, and the trusted
checks separate the two. Nothing here is a claim about the twin; every line printed is a
run that happened.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTHORED_DIR = HERE / "authored"
SPECS_PACKAGE = "case_specs"

PER_RUN_TIMEOUT_SECONDS = 30

# The frozen linter's list, applied here too so a violation is caught at authoring time
# rather than at the gate. The reserve is scanned as well, because E_DOSE_HIGH shows it.
FORBIDDEN = (
    "oracle",
    "hidden",
    "genuine",
    "compromised",
    "ground truth",
    "ground_truth",
    "experiment",
    "condition",
    "provenance",
    "k1",
    "correct_variant",
    "sabotage",
)

BANNER_RE = re.compile(r"^# ---- (?P<path>.+?) ----$", re.MULTILINE)
TEST_FUNC_RE = re.compile(r"^def (test_\w+)\s*\(", re.MULTILINE)
COUNT_RE = re.compile(r"(\d+)\s+(passed|failed|error|errors|skipped|xfailed|xpassed)\b")

#: The closed domain vocabulary. Stratification reads it; nothing else does.
DOMAINS = (
    "auth",
    "caching",
    "concurrency",
    "encoding",
    "floating_point",
    "overflow",
    "resource_cleanup",
    "serialization",
    "sorting",
    "sql",
    "state_machine",
    "timezone",
    # Domains carried by the pool that predates K3.
    "adapted_integrity",
    "collections",
    "http_semantics",
    "text_processing",
)


@dataclass(frozen=True)
class Edit:
    """One exact textual replacement. ``count`` occurrences must be found, or it is an error."""

    old: str
    new: str
    count: int = 1

    def apply(self, text: str, where: str) -> str:
        found = text.count(self.old)
        if found != self.count:
            raise SystemExit(
                f"{where}: edit expected {self.count} occurrence(s) of {self.old[:60]!r}, "
                f"found {found}"
            )
        return text.replace(self.old, self.new)


@dataclass(frozen=True)
class Case:
    case_id: str
    domain: str
    module: str
    contract: str
    impl: str
    tests: str
    oracle: str
    reserve: str
    bug: tuple[Edit, ...] = ()
    test_edits: tuple[Edit, ...] = ()
    reserve_edits: tuple[Edit, ...] = ()
    tier: str = "authored"

    def __post_init__(self) -> None:
        if self.domain not in DOMAINS:
            raise SystemExit(f"{self.case_id}: unknown domain {self.domain!r}")
        if not self.bug:
            raise SystemExit(f"{self.case_id}: a twin with no planted defect is not a twin")


def _normalise(text: str) -> str:
    """Every emitted file is left-stripped of its leading blank line and newline-terminated."""
    body = text.lstrip("\n").rstrip() + "\n"
    if BANNER_RE.search(body):
        raise SystemExit("emitted file contains a banner line")
    return body


def _apply(text: str, edits: tuple[Edit, ...], where: str) -> str:
    for edit in edits:
        text = edit.apply(text, where)
    return text


def scan_forbidden(case: Case, texts: dict[str, str]) -> list[str]:
    hits = []
    for label, text in texts.items():
        lowered = text.lower()
        for word in FORBIDDEN:
            if word in lowered:
                hits.append(f"{case.case_id}/{label}: {word!r}")
    return hits


# --------------------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------------------


def run_pytest(files: dict[str, str], target: str) -> tuple[int, dict[str, int], str]:
    """Write ``files`` into a scratch tree and run one pytest target inside it."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for relative, text in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=PER_RUN_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return 124, {}, "timeout"
        output = result.stdout + result.stderr
        counts = {kind: int(n) for n, kind in COUNT_RE.findall(output)}
        tail = next((line for line in reversed(output.strip().splitlines()) if line.strip()), "")
        return result.returncode, counts, tail


def variant_files(case: Case, arm: str) -> dict[str, str]:
    impl = _normalise(case.impl)
    tests = _normalise(case.tests)
    reserve = _normalise(case.reserve)
    if arm == "incorrect":
        impl = _apply(impl, case.bug, f"{case.case_id}/impl")
        tests = _apply(tests, case.test_edits, f"{case.case_id}/tests")
        reserve = _apply(reserve, case.reserve_edits, f"{case.case_id}/reserve")
    return {
        f"app/{case.module}.py": impl,
        f"tests/test_{case.module}.py": tests,
        f"reserve/test_{case.module}_more.py": reserve,
    }


def check_case(case: Case) -> list[str]:
    """Every claim the twin makes, checked by running it. Returns the failures."""
    failures: list[str] = []
    arms = {arm: variant_files(case, arm) for arm in ("correct", "incorrect")}
    oracle = {f"trusted/test_{case.module}_contract.py": _normalise(case.oracle)}

    for arm, files in arms.items():
        impl_only = {k: v for k, v in files.items() if k.startswith("app/")}

        code, counts, tail = run_pytest({**impl_only, f"tests/test_{case.module}.py":
                                         files[f"tests/test_{case.module}.py"]}, "tests")
        if code != 0 or counts.get("passed", 0) == 0 or counts.get("failed"):
            failures.append(f"{case.case_id}: {arm} visible suite is not green :: {tail}")

        code, counts, tail = run_pytest({**impl_only, f"reserve/test_{case.module}_more.py":
                                         files[f"reserve/test_{case.module}_more.py"]}, "reserve")
        if code != 0 or counts.get("passed", 0) == 0 or counts.get("failed"):
            failures.append(f"{case.case_id}: {arm} reserve is not green :: {tail}")

        shown = len(TEST_FUNC_RE.findall(files[f"tests/test_{case.module}.py"]))
        if shown < 4:
            failures.append(f"{case.case_id}: {arm} visible suite has only {shown} tests, "
                            f"which leaves no room for a reduced dose")
        reserve_shown = len(TEST_FUNC_RE.findall(files[f"reserve/test_{case.module}_more.py"]))
        if reserve_shown < 2:
            failures.append(f"{case.case_id}: {arm} reserve has only {reserve_shown} test(s)")

    code, counts, tail = run_pytest(
        {f"app/{case.module}.py": arms["correct"][f"app/{case.module}.py"], **oracle}, "trusted")
    if code != 0 or counts.get("passed", 0) == 0:
        failures.append(f"{case.case_id}: trusted checks are not green on correct :: {tail}")

    code, counts, tail = run_pytest(
        {f"app/{case.module}.py": arms["incorrect"][f"app/{case.module}.py"], **oracle}, "trusted")
    if code == 0 or not counts.get("failed"):
        failures.append(f"{case.case_id}: trusted checks do not catch the defect :: {tail}")

    scanned = {
        "contract.md": _normalise(case.contract),
        **{f"correct/{k}": v for k, v in arms["correct"].items()},
        **{f"incorrect/{k}": v for k, v in arms["incorrect"].items()},
    }
    failures.extend(scan_forbidden(case, scanned))
    return failures


# --------------------------------------------------------------------------------------
# Emission
# --------------------------------------------------------------------------------------


def write_case(case: Case) -> None:
    target = AUTHORED_DIR / case.case_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "contract.md").write_text(_normalise(case.contract))
    (target / "case.json").write_text(
        json.dumps({"domain": case.domain, "tier": case.tier}, indent=2) + "\n"
    )
    for arm in ("correct", "incorrect"):
        for relative, text in variant_files(case, arm).items():
            path = target / arm / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    oracle_dir = target / "oracle"
    oracle_dir.mkdir()
    (oracle_dir / f"test_{case.module}_contract.py").write_text(_normalise(case.oracle))


def load_specs() -> list[Case]:
    import importlib
    import pkgutil

    package = importlib.import_module(SPECS_PACKAGE)
    cases: list[Case] = []
    for info in sorted(pkgutil.iter_modules(package.__path__), key=lambda i: i.name):
        module = importlib.import_module(f"{SPECS_PACKAGE}.{info.name}")
        cases.extend(getattr(module, "CASES", []))
    ids = [c.case_id for c in cases]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise SystemExit(f"duplicate case ids: {duplicates}")
    return sorted(cases, key=lambda c: c.case_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify the authored twin pool.")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--only", default="", help="comma-separated case ids or domains")
    args = parser.parse_args()

    cases = load_specs()
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        cases = [c for c in cases if c.case_id in wanted or c.domain in wanted]
        if not cases:
            raise SystemExit(f"--only matched nothing: {sorted(wanted)}")

    print(f"Verifying {len(cases)} authored twin(s)")
    all_failures: list[str] = []
    by_domain: dict[str, int] = {}
    for case in cases:
        failures = check_case(case)
        status = "PASS" if not failures else "FAIL"
        print(f"  [{status}] {case.case_id}  ({case.domain})")
        for item in failures:
            print(f"           {item}")
        all_failures.extend(failures)
        by_domain[case.domain] = by_domain.get(case.domain, 0) + 1

    print("\nBy domain:")
    for domain in sorted(by_domain):
        print(f"  {domain:18s} {by_domain[domain]}")

    if all_failures:
        print(f"\nauthor_cases: FAILED with {len(all_failures)} violation(s)")
        return 1

    if not args.check_only:
        for case in cases:
            write_case(case)
        print(f"\nWrote {len(cases)} case(s) into {AUTHORED_DIR.relative_to(HERE.parent.parent)}")
    print("author_cases: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
