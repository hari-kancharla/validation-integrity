#!/usr/bin/env python3
"""Gate on the K1 case tree. Non-zero exit on any failure.

Checks, all of them printed, for every case:

1. The visible suite of ``variant_a`` passes against the ``variant_a`` implementation, and
   the same for ``variant_b``.
2. The oracle passes against the correct implementation and fails against the incorrect one.
3. None of the forbidden substrings appears in ``contract.md``, ``impl.py`` or
   ``tests_visible.py``, case-insensitively.
4. ``meta.json`` is valid, and its correct-variant letter is the one the pre-registered seed
   draws, so the truth labels cannot have been hand-edited.
5. Every suite run twice yields identical results.

Two further checks guard the honesty of what the reviewer is shown:

6. Splitting a concatenated ``impl.py`` / ``tests_visible.py`` on its banners and executing
   the recovered files is what these runs actually do, so the bytes in the payload are the
   bytes that were run. The recovered file set is reported.
7. The number of tests pytest collects equals the number of ``def test_`` functions shown,
   so the payload's "All N of N tests passed" line states a true N.

Nothing here reads or reports an oracle assertion; only its exit status is used.
"""

from __future__ import annotations

import json
import random
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"

SEED = 1337
PER_RUN_TIMEOUT_SECONDS = 20

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

BANNER_RE = re.compile(r"^# ---- (?P<path>.+?) ----$")
TEST_FUNC_RE = re.compile(r"^def (test_\w+)\s*\(", re.MULTILINE)
COUNT_RE = re.compile(r"(\d+)\s+(passed|failed|error|errors|skipped|xfailed|xpassed)\b")


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, label: str, ok: bool, detail: str = "") -> bool:
        status = "PASS" if ok else "FAIL"
        suffix = f" :: {detail}" if detail else ""
        print(f"  [{status}] {label}{suffix}")
        if not ok:
            self.failures.append(f"{label}{suffix}")
        return ok


def split_concatenated(document: str) -> dict[str, str]:
    files: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    for line in document.splitlines(keepends=True):
        match = BANNER_RE.match(line.rstrip("\n"))
        if match:
            if current is not None:
                files[current] = "".join(buffer)
            current = match.group("path")
            buffer = []
            continue
        if current is None:
            raise ValueError("concatenated document has content before its first banner")
        buffer.append(line)
    if current is not None:
        files[current] = "".join(buffer)
    return files


def materialize(root: Path, documents: list[str]) -> list[str]:
    written: list[str] = []
    for document in documents:
        for relative, text in split_concatenated(document).items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
            written.append(relative)
    return sorted(written)


def run_suite(documents: list[str], target: str) -> tuple[int, Counter, float, str]:
    """Reconstruct a workspace from concatenated documents and run one pytest target."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        materialize(root, documents)
        started = time.monotonic()
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=PER_RUN_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return 124, Counter(), float(PER_RUN_TIMEOUT_SECONDS), "timeout"
        elapsed = time.monotonic() - started
        output = result.stdout + result.stderr
        counts = Counter({kind: int(n) for n, kind in COUNT_RE.findall(output)})
        tail = next(
            (line for line in reversed(output.strip().splitlines()) if line.strip()), ""
        )
        return result.returncode, counts, elapsed, tail


def summarize(counts: Counter) -> str:
    return ", ".join(f"{counts[k]} {k}" for k in sorted(counts)) or "no counts"


def lint_case(case_dir: Path, expected_letter: str, report: Report) -> None:
    case_id = case_dir.name
    print(f"\n{case_id}")

    # --- check 4: meta.json -------------------------------------------------------
    meta_ok = True
    try:
        meta = json.loads((case_dir / "meta.json").read_text())
    except Exception as exc:  # noqa: BLE001 - reported, not swallowed
        report.check("meta.json is valid JSON", False, str(exc))
        return
    meta_ok &= report.check("meta.json is valid JSON", True)
    meta_ok &= report.check(
        "meta.json case_id matches directory", meta.get("case_id") == case_id
    )
    letter = meta.get("correct_variant")
    meta_ok &= report.check(
        "meta.json correct_variant is 'a' or 'b'", letter in ("a", "b"), f"value={letter!r}"
    )
    meta_ok &= report.check("meta.json seed is the pre-registered seed", meta.get("seed") == SEED)
    meta_ok &= report.check(
        "meta.json correct_variant matches the seeded draw",
        letter == expected_letter,
        f"meta={letter!r} seeded={expected_letter!r}",
    )
    if not meta_ok or letter not in ("a", "b"):
        return
    incorrect_letter = "b" if letter == "a" else "a"

    contract = (case_dir / "contract.md").read_text()
    impl = {v: (case_dir / f"variant_{v}" / "impl.py").read_text() for v in ("a", "b")}
    tests = {v: (case_dir / f"variant_{v}" / "tests_visible.py").read_text() for v in ("a", "b")}
    oracle = (case_dir / "oracle" / "tests_hidden.py").read_text()

    # --- check 3: forbidden substrings in the visible artifacts -------------------
    for label, text in (
        ("contract.md", contract),
        ("variant_a/impl.py", impl["a"]),
        ("variant_b/impl.py", impl["b"]),
        ("variant_a/tests_visible.py", tests["a"]),
        ("variant_b/tests_visible.py", tests["b"]),
    ):
        lowered = text.lower()
        hits = [word for word in FORBIDDEN if word in lowered]
        report.check(f"no forbidden substring in {label}", not hits, ", ".join(hits))

    # --- check 6: the concatenation is reversible ---------------------------------
    for variant in ("a", "b"):
        try:
            recovered = sorted(
                list(split_concatenated(impl[variant])) + list(split_concatenated(tests[variant]))
            )
            report.check(
                f"variant_{variant} splits back into source files",
                len(recovered) == len(set(recovered)) and bool(recovered),
                ", ".join(recovered),
            )
        except ValueError as exc:
            report.check(f"variant_{variant} splits back into source files", False, str(exc))

    # --- checks 1 and 5: visible suites, run twice --------------------------------
    for variant in ("a", "b"):
        runs = [run_suite([impl[variant], tests[variant]], "tests") for _ in range(2)]
        (code, counts, elapsed, tail) = runs[0]
        report.check(
            f"variant_{variant} visible suite passes on its own implementation",
            code == 0 and counts.get("passed", 0) > 0 and not counts.get("failed"),
            f"exit={code}, {summarize(counts)}, {elapsed:.2f}s",
        )
        report.check(
            f"variant_{variant} visible suite finishes well inside {PER_RUN_TIMEOUT_SECONDS}s",
            elapsed < PER_RUN_TIMEOUT_SECONDS,
            f"{elapsed:.2f}s",
        )
        report.check(
            f"variant_{variant} visible suite is deterministic across two runs",
            (runs[0][0], runs[0][1]) == (runs[1][0], runs[1][1]),
            f"{summarize(runs[0][1])} vs {summarize(runs[1][1])}",
        )
        # --- check 7: the stated N would be truthful ------------------------------
        shown = len(TEST_FUNC_RE.findall(tests[variant]))
        collected = counts.get("passed", 0) + counts.get("failed", 0) + counts.get("skipped", 0)
        report.check(
            f"variant_{variant} collected test count equals the shown function count",
            shown == collected and shown > 0,
            f"shown={shown} collected={collected}",
        )

    # --- checks 2 and 5: the oracle separates the two variants --------------------
    correct_runs = [run_suite([impl[letter], oracle], "trusted_oracle") for _ in range(2)]
    report.check(
        "oracle passes against the correct implementation",
        correct_runs[0][0] == 0 and correct_runs[0][1].get("passed", 0) > 0,
        f"exit={correct_runs[0][0]}, {summarize(correct_runs[0][1])}",
    )
    report.check(
        "oracle is deterministic on the correct implementation",
        (correct_runs[0][0], correct_runs[0][1]) == (correct_runs[1][0], correct_runs[1][1]),
    )

    incorrect_runs = [run_suite([impl[incorrect_letter], oracle], "trusted_oracle") for _ in range(2)]
    report.check(
        "oracle fails against the incorrect implementation",
        incorrect_runs[0][0] != 0 and incorrect_runs[0][1].get("failed", 0) > 0,
        f"exit={incorrect_runs[0][0]}, {summarize(incorrect_runs[0][1])}",
    )
    report.check(
        "oracle is deterministic on the incorrect implementation",
        (incorrect_runs[0][0], incorrect_runs[0][1]) == (incorrect_runs[1][0], incorrect_runs[1][1]),
    )


def main() -> int:
    if not CASES_DIR.is_dir():
        print(f"lint_cases: no case tree at {CASES_DIR}; run build_payloads.py first")
        return 1
    case_ids = sorted(p.name for p in CASES_DIR.iterdir() if p.is_dir())
    if not case_ids:
        print("lint_cases: case tree is empty")
        return 1

    rng = random.Random(SEED)
    expected = {case_id: rng.choice(("a", "b")) for case_id in case_ids}

    report = Report()
    for case_id in case_ids:
        lint_case(CASES_DIR / case_id, expected[case_id], report)

    print(f"\nlint_cases: {len(case_ids)} case(s) checked")
    if report.failures:
        print(f"lint_cases: FAILED with {len(report.failures)} violation(s)")
        for item in report.failures:
            print(f"  - {item}")
        return 1
    print("lint_cases: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
