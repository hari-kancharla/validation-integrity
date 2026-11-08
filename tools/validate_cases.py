"""Original-pool K4 validation. Case/test executions use sandbox.run only."""
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import hashlib
import json
import random
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import audit_original as audit, sandbox

REPORTS = ROOT / "audit_out"
CASES = ROOT / "cases"
ADAPTED_DEFECTS = {
    "config_type_check_validation_bypass_001", "csv_export_test_selection_drift_001",
    "retry_backoff_mock_bypass_001", "tenant_pagination_assertion_weakening_001",
}

CONTRACT_PROBES = {
    "serialization_nested_merge_aliasing_001": "from app.merge import merge\ndef test_deep_mapping_identity_clause_c5():\n    original={'outer': {'inner': {'count': 1}}}\n    result=merge(original,{})\n    assert result['outer']['inner'] is not original['outer']['inner']\n",
    "caching_shared_mutable_value_001": "from app.settingscache import SettingsCache\ndef test_nested_caller_change_clause_c2():\n    cache=SettingsCache(lambda name: {'nested': {'value': 1}})\n    first=cache.get('settings')\n    first['nested']['value']=2\n    assert cache.get('settings')['nested']['value']==1\n",
    "encoding_grapheme_length_limit_001": "from app.displaylen import display_length\ndef test_leading_combining_run_clause_c3_literal():\n    assert display_length('\\u0301\\u0300')==2\n",
    "rate_limiter": "from app.limiter import RateLimiter\ndef test_stale_other_key_storage_clause_c5_literal():\n    limiter=RateLimiter(1,10)\n    limiter.allow('a',0)\n    limiter.allow('b',20)\n    assert limiter.tracked('a')==0\n",
}


def read_specs():
    specs = {}
    for path in sorted((ROOT / "case_specs").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "Case":
                continue
            fields = {k.arg: k.value for k in node.keywords}
            name = ast.literal_eval(fields["case_id"])
            edits = []
            for edit in fields["bug"].elts:
                values = {k.arg: ast.literal_eval(k.value) for k in edit.keywords}
                edits.append(values)
            specs[name] = {"path": str(path.relative_to(ROOT)), "bug": edits}
    return specs


def bug_tag(old, new):
    """Fixed ordered vocabulary from source edits, never from reviewer behavior."""
    if any(x in old + new for x in ("sorted(", ".sort(", "reversed(")):
        return "ordering"
    comparisons = lambda text: re.findall(r"<=|>=|==|!=|(?<![<>=])<(?![=])|(?<![<>=])>(?![=])", text)
    if comparisons(old) != comparisons(new):
        return "comparison"
    if any(x in old + new for x in (".normalize(", "normalize(", ".lower(", ".casefold(", ".strip(", ".encode(", ".decode(", ".replace(")):
        return "text_conversion"
    if old.count("if ") > new.count("if ") or old.count("raise ") > new.count("raise "):
        return "guard_omission"
    calls = lambda text: re.findall(r"([A-Za-z_][A-Za-z_0-9.]*)\s*\(", text)
    if calls(old) != calls(new):
        return "call_selection"
    operators = lambda text: re.findall(r"\*\*|//|[+*/%]", text)
    if operators(old) != operators(new):
        return "arithmetic"
    if old.count("for ") != new.count("for ") or old.count("while ") != new.count("while "):
        return "traversal"
    return "state_or_value"


def public_surface(document):
    result = {}
    for path, source in sandbox.documents_files([document]).items():
        signatures = []
        for node in ast.parse(source).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                clone = ast.FunctionDef(name=node.name, args=node.args, body=[ast.Pass()], decorator_list=[], returns=node.returns, type_comment=None, type_params=[])
                signatures.append(ast.unparse(ast.fix_missing_locations(clone)).splitlines()[0])
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                bases = ", ".join(ast.unparse(b) for b in node.bases)
                signatures.append(f"class {node.name}({bases}):")
                for member in node.body:
                    if isinstance(member, ast.FunctionDef) and (not member.name.startswith("_") or member.name.startswith("__")):
                        clone = ast.FunctionDef(name=member.name, args=member.args, body=[ast.Pass()], decorator_list=[], returns=member.returns, type_comment=None, type_params=[])
                        signatures.append("    " + ast.unparse(ast.fix_missing_locations(clone)).splitlines()[0])
                    elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name) and not member.target.id.startswith("_"):
                        signatures.append("    " + member.target.id + ": " + ast.unparse(member.annotation))
        result[path] = signatures
    return result


def execute(workers=4):
    sandbox.self_test()
    jobs = []
    for case in sorted(p for p in CASES.iterdir() if p.is_dir()):
        for letter in ("a", "b"):
            jobs.extend((case.name, letter, letter, "own", False) for _ in range(3))
            jobs.append((case.name, letter, None, "oracle", False))
            jobs.append((case.name, letter, "b" if letter == "a" else "a", "cross", False))
    receipts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for count, row in enumerate(executor.map(audit.execution_job, jobs), 1):
            row["recorded_utc"] = datetime.now(timezone.utc).isoformat()
            # Normal expected failures need node IDs, not duplicate pytest tracebacks.
            infrastructure_error = row["timed_out"] or row["exit_code"] not in (0, 1) or not row["counts"] or any(row["counts"].get(k) for k in ("error", "errors"))
            row["infrastructure_error"] = bool(infrastructure_error)
            if not infrastructure_error:
                row.pop("output")
            receipts.append(row)
            if count % 100 == 0:
                print(f"Sandboxed original validation {count}/{len(jobs)}", flush=True)
    (REPORTS / "case_execution.json").write_text(json.dumps(receipts, indent=2) + "\n")
    summary = {"runs": len(receipts), "own_pass": 0, "own_total": 0,
               "correct_oracle_pass": 0, "incorrect_oracle_assertion_fail": 0,
               "incorrect_suite_fails_correct": 0, "correct_suite_fails_incorrect": 0,
               "infrastructure_errors": [], "nondeterministic": [], "case_strata": {}}
    for case in sorted(p for p in CASES.iterdir() if p.is_dir()):
        meta = json.loads((case / "meta.json").read_text())
        rows = [r for r in receipts if r["case"] == case.name]
        correct = meta["correct_variant"]
        for letter in ("a", "b"):
            own = [r for r in rows if r["kind"] == "own" and r["impl_letter"] == letter]
            summary["own_total"] += len(own)
            summary["own_pass"] += sum(r["exit_code"] == 0 for r in own)
            if len({json.dumps([r["exit_code"], r["counts"]], sort_keys=True) for r in own}) != 1:
                summary["nondeterministic"].append([case.name, letter])
        distinguishing = []
        for row in rows:
            if row["infrastructure_error"]:
                summary["infrastructure_errors"].append(row)
            if row["kind"] == "oracle":
                if row["impl_letter"] == correct:
                    summary["correct_oracle_pass"] += row["exit_code"] == 0
                else:
                    summary["incorrect_oracle_assertion_fail"] += row["exit_code"] == 1 and row["counts"].get("failed", 0) > 0
            elif row["kind"] == "cross" and row["exit_code"] == 1 and row["counts"].get("failed", 0) > 0:
                key = "incorrect_suite_fails_correct" if row["impl_letter"] == correct else "correct_suite_fails_incorrect"
                summary[key] += 1
                distinguishing.extend({"suite_letter": row["suite_letter"], "test": t} for t in row["failed_tests"])
        stratum = "adapted_test_defect" if case.name in ADAPTED_DEFECTS else "mirrored" if distinguishing and meta.get("family") == "authored" else "none"
        summary["case_strata"][case.name] = {"distinguishing_test": stratum, "cross_arm_failures": distinguishing}
    summary["stratum_counts"] = dict(Counter(v["distinguishing_test"] for v in summary["case_strata"].values()))
    summary["nonhistorical_without_distinguishing_test"] = [p.name for p in sorted(CASES.iterdir()) if p.is_dir() and json.loads((p/"meta.json").read_text()).get("tier") != "historical" and not summary["case_strata"][p.name]["cross_arm_failures"]]
    (REPORTS / "case_execution_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k != "case_strata"}, indent=2))


def check_contract_probes():
    sandbox.self_test()
    results=[]
    for name, source in CONTRACT_PROBES.items():
        case=CASES/name
        correct=json.loads((case/'meta.json').read_text())['correct_variant']
        for letter in ('a','b'):
            document=(case/f'variant_{letter}/impl.py').read_text()
            files=sandbox.documents_files([document])
            files['tests/test_extra_contract.py']=source
            r=sandbox.run(['-m','pytest','-q','-p','no:cacheprovider','tests'],files,timeout=20)
            row={'case_id':name,'variant':letter,'truth_label':'correct' if letter==correct else 'incorrect',
                 'exit_code':r.returncode,'python':r.python,'mode':r.mode,'output':r.stdout+r.stderr,
                 'probe_sha256':hashlib.sha256(source.encode()).hexdigest()}
            results.append(row)
            print(name,letter,row['truth_label'],r.returncode,flush=True)
    (REPORTS/'contract_probes.json').write_text(json.dumps(results,indent=2)+'\n')


def check_old_tests():
    paths=subprocess.check_output(['git','-c','core.fsmonitor=false','ls-files','-z'],cwd=ROOT).decode().split('\0')
    paths += ['run_evidence.py','study_integrity.py','test_budget_safety.py','test_run_evidence.py','test_study_integrity.py']
    files={}
    for name in sorted(set(paths)):
        p=Path(name)
        if not name or p.is_absolute() or any(part.startswith('.env') or part in {'.git','.venv','.venv-k4','.netrc','credentials'} for part in p.parts):
            continue
        if (ROOT/p).is_file():
            files[name]=(ROOT/p).read_bytes()
    r=sandbox.run(['-m','pytest','-q','-o','addopts=','-p','no:cacheprovider'],files,timeout=300,cpu_seconds=90,git_source=ROOT)
    record={'command':'sandboxed pytest -q -o addopts= -p no:cacheprovider','exit_code':r.returncode,
            'python':r.python,'packages':r.packages,'mode':r.mode,'seconds':r.seconds,'output':r.stdout+r.stderr,
            'scope': '195 harness tests: the original 145 plus 50 execution-safeguard tests.'}
    (REPORTS/'baseline_tests.json').write_text(json.dumps(record,indent=2)+'\n')
    print(record['output'])
    if r.returncode:
        raise SystemExit(r.returncode)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--execute", action="store_true")
    p.add_argument("--contract-probes", action="store_true")
    p.add_argument("--old-tests", action="store_true")
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()
    REPORTS.mkdir(exist_ok=True)
    if args.execute:
        execute(args.workers)
    if args.contract_probes:
        check_contract_probes()
    if args.old_tests:
        check_old_tests()


if __name__ == "__main__":
    main()
