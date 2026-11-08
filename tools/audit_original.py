#!/usr/bin/env python3
"""Read-only source/surface audit; execution_job delegates to the K4 sandbox."""
from __future__ import annotations

import argparse
import ast
import collections
import difflib
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tokenize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit_out"
sys.path.insert(0, str(ROOT))
import lint_cases

BANNER = re.compile(r"^# ---- .+ ----$")
COUNT = re.compile(r"(\d+)\s+(passed|failed|error|errors|skipped|xfailed|xpassed)\b")


def split(text):
    return lint_cases.split_concatenated(text)


def test_nodes(text):
    return [(p, n) for p, body in split(text).items() for n in ast.parse(body).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")]


def full_comments(text):
    return [t for t in tokenize.generate_tokens(io.StringIO(text).readline)
            if t.type == tokenize.COMMENT and not t.line[:t.start[1]].strip()]


def in_function_comments(text):
    count = 0
    for body in split(text).values():
        spans = [(n.lineno, n.end_lineno) for n in ast.walk(ast.parse(body))
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        comments = [t for t in tokenize.generate_tokens(io.StringIO(body).readline) if t.type == tokenize.COMMENT]
        count += sum(any(start < t.start[0] <= end for start, end in spans) for t in comments)
    return count


def docstrings(text):
    return sum(ast.get_docstring(n, clean=False) is not None
               for body in split(text).values() for n in ast.walk(ast.parse(body))
               if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)))


def unused(text):
    """Pyflakes unused imports/locals plus unreferenced uppercase module constants.

    This is a syntactic count, not a claim of removable public API: callers can
    import constants or inspect function locals indirectly.
    """
    from pyflakes.checker import Checker
    found = []
    for path, body in split(text).items():
        tree = ast.parse(body)
        check = Checker(tree, filename=path)
        for msg in check.messages:
            if type(msg).__name__ in {"UnusedImport", "UnusedVariable"}:
                found.append({"file": path, "line": msg.lineno,
                              "kind": type(msg).__name__, "name": str(msg.message_args[0])})
        loaded = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        for n in tree.body:
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id.isupper() and target.id not in loaded:
                        found.append({"file": path, "line": n.lineno, "kind": "UnusedModuleConstant", "name": target.id})
    return found


def type_only(n):
    assertions = [a for a in ast.walk(n) if isinstance(a, ast.Assert)]
    return bool(assertions) and all(isinstance(a.test, ast.Call)
        and isinstance(a.test.func, ast.Name) and a.test.func.id == "isinstance" for a in assertions)


def ast_tests(text):
    return {n.name: ast.dump(n, include_attributes=False) for _, n in test_nodes(text)}






def features(payload):
    blocks = re.findall(r"```python\n(.*?)```", payload, re.S)
    impl = blocks[0] if blocks else ""
    tests = blocks[1] if len(blocks) > 1 else ""
    text = impl + tests
    trees = [ast.parse(body) for block in [impl, tests] if block for body in split(block).values()]
    nodes = [n for tree in trees for n in ast.walk(tree)]
    status = re.search(r"All (\d+) of \d+ tests passed", payload)
    return {
        "payload_chars": len(payload), "impl_chars": len(impl), "tests_chars": len(tests),
        "comment_lines": len(full_comments(text)),
        "function_comment_lines": sum(in_function_comments(b) for b in [impl, tests] if b),
        "docstrings": sum(docstrings(b) for b in [impl, tests] if b),
        "N": int(status.group(1)) if status else 0,
        "functions": sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in nodes),
        "imports": sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in nodes),
        "asserts": sum(isinstance(n, ast.Assert) for n in nodes),
        "isinstance_calls": sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "isinstance" for n in nodes),
        "max_line_length": max(map(len, text.splitlines()), default=0),
        "unused_names": sum(len(unused(b)) for b in [impl, tests] if b),
        "distinct_identifiers": len({n.id for n in nodes if isinstance(n, ast.Name)}),
    }


def classifiers(exclude_historical=False):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, accuracy_score
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits
    threadpool_limits(limits=1)
    results = {}
    all_rows = []
    for condition in ["E_NONE", "E_COUPLED"]:
        rows = []
        for case in sorted((ROOT / "cases").iterdir()):
            if not case.is_dir():
                continue
            meta = json.loads((case / "meta.json").read_text())
            if exclude_historical and meta.get("tier") == "historical":
                continue
            for variant in ["a", "b"]:
                p = ROOT / "payloads" / case.name / variant / f"{condition}.md"
                if p.exists():
                    payload = p.read_text()
                    rows.append({"case": case.name, "variant": variant,
                                 "incorrect": int(variant != meta["correct_variant"]),
                                 "features": features(payload)})
        names = list(rows[0]["features"])
        X = np.array([[r["features"][n] for n in names] for r in rows], dtype=float)
        y = np.array([r["incorrect"] for r in rows])
        groups = np.array([r["case"] for r in rows])
        prediction = np.empty(len(y))
        for case in sorted(set(groups)):
            holdout = groups == case
            scaler = StandardScaler().fit(X[~holdout])
            model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=3000)
            model.fit(scaler.transform(X[~holdout]), y[~holdout])
            prediction[holdout] = model.predict_proba(scaler.transform(X[holdout]))[:, 1]
        cases = sorted(set(groups))
        rng = np.random.RandomState(1337)
        aucs = []
        for _ in range(2000):
            sample = rng.choice(cases, size=len(cases), replace=True)
            ix = np.concatenate([np.flatnonzero(groups == c) for c in sample])
            aucs.append(float(roc_auc_score(y[ix], prediction[ix])))
        ranks = []
        for case in cases:
            ix = np.flatnonzero(groups == case)
            if len(ix) == 2 and set(y[ix]) == {0, 1}:
                good, bad = prediction[ix[y[ix] == 0]][0], prediction[ix[y[ix] == 1]][0]
                ranks.append(1.0 if bad > good else 0.5 if bad == good else 0.0)
        single = {}
        for i, name in enumerate(names):
            auc = float(roc_auc_score(y, X[:, i]))
            single[name] = {"raw_auc_incorrect_positive": auc, "direction_free_auc": max(auc, 1 - auc)}
        results[condition] = {"n_payloads": len(rows), "n_cases": len(cases),
            "accuracy": float(accuracy_score(y, prediction >= .5)),
            "auroc": float(roc_auc_score(y, prediction)),
            "auroc_case_bootstrap_95ci": np.quantile(aucs, [.025, .975]).tolist(),
            "within_case_pair_ranking_accuracy_ties_half": float(np.mean(ranks)),
            "single_feature_auc": single}
        for row, pred in zip(rows, prediction):
            all_rows.append({"condition": condition, **row, "oof_score": float(pred)})
        print(condition, {k: results[condition][k] for k in (
            "n_cases", "accuracy", "auroc", "auroc_case_bootstrap_95ci",
            "within_case_pair_ranking_accuracy_ties_half")}, flush=True)
    stem = "original"
    if exclude_historical:
        stem += "_excluding_historical"
    (OUT / f"{stem}_classifier.json").write_text(json.dumps(results, indent=2) + "\n")
    (OUT / f"{stem}_features.json").write_text(json.dumps(all_rows, indent=2) + "\n")
    return results


def static():
    records = []
    visible = []
    reserves = []
    for case in sorted((ROOT / "cases").iterdir()):
        if not case.is_dir():
            continue
        meta = json.loads((case / "meta.json").read_text())
        letters = {"correct": meta["correct_variant"], "incorrect": "b" if meta["correct_variant"] == "a" else "a"}
        arms = {}
        for truth, letter in letters.items():
            variant = case / f"variant_{letter}"
            impl = (variant / "impl.py").read_text()
            tests = (variant / "tests_visible.py").read_text()
            nodes = test_nodes(tests)
            vis = [{"case": case.name, "truth": truth, "name": n.name, "type_only": type_only(n), "contains_isinstance": any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "isinstance" for x in ast.walk(n)), "lines": n.end_lineno - n.lineno + 1} for _, n in nodes]
            visible.extend(vis)
            reserve = variant / "reserve.py"
            if reserve.exists():
                reserves.extend({"case": case.name, "truth": truth, "name": n.name, "type_only": type_only(n), "contains_isinstance": any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "isinstance" for x in ast.walk(n)), "lines": n.end_lineno - n.lineno + 1} for _, n in test_nodes(reserve.read_text()))
            coupled = (ROOT / "payloads" / case.name / letter / "E_COUPLED.md").read_text()
            lowpath = ROOT / "payloads" / case.name / letter / "E_DOSE_LOW.md"
            arms[truth] = {"letter": letter, "impl_full_line_comments": len(full_comments(impl)),
                "impl_function_comments": in_function_comments(impl), "test_count": len(nodes),
                "test_docstring_count": sum(ast.get_docstring(n, clean=False) is not None for _, n in nodes),
                "test_names": [n.name for _, n in nodes], "test_asts": ast_tests(tests),
                "impl_unused": unused(impl), "suite_unused": unused(tests),
                "coupled_chars": len(coupled), "none_chars": len((ROOT / "payloads" / case.name / letter / "E_NONE.md").read_text()),
                "impl_chars": len(impl), "impl_bytes": len(impl.encode()),
                "stated_N": int(re.search(r"All (\d+) of \d+", coupled).group(1)),
                "low_names": re.findall(r"^def (test_\w+)\s*\(", lowpath.read_text(), re.M) if lowpath.exists() else None}
        c, b = arms["correct"], arms["incorrect"]
        b["unique_names"] = [n for n in b["test_names"] if n not in c["test_names"]]
        b["unique_asts"] = [n for n in b["test_names"] if b["test_asts"][n] != c["test_asts"].get(n)]
        records.append({"case": case.name, "family": meta.get("family"), "tier": meta.get("tier"), "arms": arms})
    high = list((ROOT / "payloads").glob("*/*/E_DOSE_HIGH.md"))
    hist = next(r for r in records if r["tier"] == "historical")
    hc = ROOT / "cases" / hist["case"]
    ia = (hc / "variant_a" / "impl.py").read_text()
    ib = (hc / "variant_b" / "impl.py").read_text()
    summary = {
      "n_cases": len(records), "composition_family": dict(collections.Counter(r["family"] for r in records)),
      "1_incorrect_more_impl_full_line_comments": sum(r["arms"]["incorrect"]["impl_full_line_comments"] > r["arms"]["correct"]["impl_full_line_comments"] for r in records),
      "1_incorrect_fewer_impl_full_line_comments": sum(r["arms"]["incorrect"]["impl_full_line_comments"] < r["arms"]["correct"]["impl_full_line_comments"] for r in records),
      "2_cases_impl_function_comments": {t: sum(r["arms"][t]["impl_function_comments"] > 0 for r in records) for t in ["correct", "incorrect"]},
      "3_incorrect_test_count_comparison": {op: sum((r["arms"]["incorrect"]["test_count"] > r["arms"]["correct"]["test_count"] if op == "more" else r["arms"]["incorrect"]["test_count"] < r["arms"]["correct"]["test_count"] if op == "fewer" else r["arms"]["incorrect"]["test_count"] == r["arms"]["correct"]["test_count"]) for r in records) for op in ["more", "equal", "fewer"]},
      "4_test_docstrings": {t: {"test_functions": sum(r["arms"][t]["test_count"] for r in records), "docstrings": sum(r["arms"][t]["test_docstring_count"] for r in records), "suites": sum(r["arms"][t]["test_docstring_count"] > 0 for r in records)} for t in ["correct", "incorrect"]},
      "7_cases_unused_nonhistorical_impl": {t: sum(bool(r["arms"][t]["impl_unused"]) for r in records if r["tier"] != "historical") for t in ["correct", "incorrect"]},
      "7_cases_unused_nonhistorical_impl_and_suite": {t: sum(bool(r["arms"][t]["impl_unused"] + r["arms"][t]["suite_unused"]) for r in records if r["tier"] != "historical") for t in ["correct", "incorrect"]},
      "8_unique_test_last": {}, "9_low_drops_unique": {},
      "10_type_only": {"visible": {"type_only": sum(r["type_only"] for r in visible), "total": len(visible)}, "reserve": {"type_only": sum(r["type_only"] for r in reserves), "total": len(reserves)}},
      "10_contains_isinstance": {"visible": {"contains": sum(r["contains_isinstance"] for r in visible), "total": len(visible)}, "reserve": {"contains": sum(r["contains_isinstance"] for r in reserves), "total": len(reserves)}},
      "10_per_truth_arm": {t: {label: {"total": sum(r["truth"] == t for r in rows), "direct_isinstance_only": sum(r["truth"] == t and r["type_only"] for r in rows), "contains_isinstance": sum(r["truth"] == t and r["contains_isinstance"] for r in rows)} for label, rows in [("visible", visible), ("reserve", reserves)]} for t in ["correct", "incorrect"]},
      "11_reserve_header_high": {"with_header": sum(bool(re.search(r"^# ---- reserve/.+ ----$", p.read_text(), re.M)) for p in high), "total": len(high)},
      "12_incorrect_coupled_longer": sum(r["arms"]["incorrect"]["coupled_chars"] > r["arms"]["correct"]["coupled_chars"] for r in records),
      "13_stated_N_distribution": {t: dict(collections.Counter(r["arms"][t]["stated_N"] for r in records)) for t in ["correct", "incorrect"]},
      "15_historical": {"case": hist["case"], "impl_chars": {t: hist["arms"][t]["impl_chars"] for t in ["correct", "incorrect"]}, "impl_bytes": {t: hist["arms"][t]["impl_bytes"] for t in ["correct", "incorrect"]}, "none_fraction": sum(hist["arms"][t]["none_chars"] for t in ["correct", "incorrect"]) / sum(r["arms"][t]["none_chars"] for r in records for t in ["correct", "incorrect"]), "sequence_diff": [x for x in difflib.ndiff(ia.splitlines(), ib.splitlines()) if x.startswith(("+ ", "- "))]},
      "16_correct_letter_balance": dict(collections.Counter(r["arms"]["correct"]["letter"] for r in records)),
      "average_lines_per_test": {"visible": sum(r["lines"] for r in visible) / len(visible), "reserve": sum(r["lines"] for r in reserves) / len(reserves)},
    }
    for definition in ["unique_names", "unique_asts"]:
        unique = [r for r in records if r["arms"]["incorrect"][definition]]
        summary["8_unique_test_last"][definition] = {"last": sum(r["arms"]["incorrect"]["test_names"][-1] in r["arms"]["incorrect"][definition] for r in unique), "cases_with_unique": len(unique)}
        low = [r for r in records if r["arms"]["incorrect"]["low_names"] is not None]
        summary["9_low_drops_unique"][definition] = {"drops_all_including_empty_set": sum(not set(r["arms"]["incorrect"][definition]) & set(r["arms"]["incorrect"]["low_names"]) for r in low), "available_low_cells": len(low), "nonempty_unique_cells": sum(bool(r["arms"]["incorrect"][definition]) for r in low), "drops_all_nonempty": sum(bool(r["arms"]["incorrect"][definition]) and not set(r["arms"]["incorrect"][definition]) & set(r["arms"]["incorrect"]["low_names"]) for r in low)}
    (OUT / "static_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "static_cases.json").write_text(json.dumps([{**r, "arms": {t: {k:v for k,v in a.items() if k != "test_asts"} for t,a in r["arms"].items()}} for r in records], indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


def execution_job(job):
    case_id, implementation_letter, suite_letter, kind, cleaned = job
    case = ROOT / "cases" / case_id
    impl = (case / f"variant_{implementation_letter}" / "impl.py").read_text()
    if kind in ["E_DOSE_LOW", "E_DOSE_HIGH"]:
        payload = (ROOT / "payloads" / case_id / implementation_letter / f"{kind}.md").read_text()
        suite = re.findall(r"```python\n(.*?)```", payload, re.S)[1]
    else:
        suite = ((case / "oracle" / "tests_hidden.py") if kind == "oracle" else (case / f"variant_{suite_letter}" / ("reserve.py" if kind == "reserve" else "tests_visible.py"))).read_text()
    if cleaned:
        raise ValueError("Superseded all-docstring cleaning path is disabled")
    from tools import sandbox
    targets = ["trusted_oracle"] if kind == "oracle" else ["reserve"] if kind == "reserve" else ["tests", "reserve"] if kind == "E_DOSE_HIGH" else ["tests"]
    process = sandbox.run(["-m", "pytest", "-q", "-p", "no:cacheprovider", *targets], sandbox.documents_files([impl, suite]), timeout=30, cpu_seconds=20)
    output = process.stdout + process.stderr
    return {"case": case_id, "impl_letter": implementation_letter, "suite_letter": suite_letter, "kind": kind, "cleaned": cleaned,
            "exit_code": process.returncode, "counts": dict(collections.Counter({kind: int(n) for n, kind in COUNT.findall(output)})),
            "failed_tests": re.findall(r"^FAILED (\S+)", output, re.M), "timed_out": process.timed_out,
            "mode": process.mode, "python": process.python, "seconds": process.seconds,
            "impl_sha256": hashlib.sha256(impl.encode()).hexdigest(), "suite_sha256": hashlib.sha256(suite.encode()).hexdigest(),
            "output": output}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--classifier", action="store_true")
    parser.add_argument("--exclude-historical", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.static:
        static()
    if args.classifier:
        classifiers(exclude_historical=args.exclude_historical)
