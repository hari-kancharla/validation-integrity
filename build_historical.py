#!/usr/bin/env python3
"""Derive the historical twin tier from the repository's own ingested bug fixes.

`arena import-fix` has already turned each upstream buggy/fixed commit pair into a pack
under ``benchmark_sets/realfix_seed_v0``: ``before/`` is the source at the fixed commit,
``after/`` is the source at the buggy commit, and ``tests/`` is the project's own test tree
at the fixed commit. This module maps a pack onto the K1 twin layout:

    correct   = before/   (post-fix source)
    incorrect = after/    (pre-fix source)
    visible   = the project's own tests that are green on BOTH arms
    trusted   = the project's own tests that are green on before and red on after

Which test belongs to which set is decided **by running them**, never by reading a commit
message. A test that the fix repaired is red on the pre-fix source by definition, so the
split falls out of two executions and nothing is hand-assigned.

Two mechanical transforms make a pack fit the frozen gate, and neither changes an assertion:

``de-parametrize``
    ``@pytest.mark.parametrize`` is rewritten into a loop over the same argument list inside
    the same function. Every input value and every assertion is carried over verbatim; only
    pytest's plumbing changes. This is what lets ``lint_cases.py``'s check 7 hold, since the
    payload's "All N of N tests passed" line must state the number of test functions shown.

``import closure``
    Only the modules the changed source and the chosen tests actually import are carried,
    computed with ``ast``. Everything shown is executed and everything executed is shown.

A pack that cannot be made to fit is refused with a recorded reason, never bent to fit.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
PACKS_DIR = REPO_ROOT / "benchmark_sets" / "realfix_seed_v0"
SOURCES_DIR = REPO_ROOT / "benchmark_sources" / "realfix_seed_v0"
HISTORICAL_DIR = HERE / "historical"

#: The implementation is rendered in full inside the payload, so it has to be showable.
MAX_IMPL_BYTES = 400_000
MAX_TESTS_BYTES = 80_000

MIN_VISIBLE_TESTS = 3
MIN_RESERVE_TESTS = 2
MIN_TRUSTED_TESTS = 1

RUN_TIMEOUT_SECONDS = 600

FORBIDDEN = (
    "oracle", "hidden", "genuine", "compromised", "ground truth", "ground_truth",
    "experiment", "condition", "provenance", "k1", "correct_variant", "sabotage",
)

BANNER_RE = re.compile(r"^# ---- (?P<path>.+?) ----$", re.MULTILINE)
TEST_FUNC_RE = re.compile(r"^def (test_\w+)\s*\(", re.MULTILINE)
OUTCOME_RE = re.compile(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS) (\S+)", re.MULTILINE)



#: A specification for each admitted historical case, written from the post-fix behaviour of
#: the public surface its shown tests exercise. It names an API and what that API owes its
#: callers; it never names a defect, a commit or a variant.
CONTRACTS = {
    "packaging_name_validation_newline_001": """
## Canonical names, versions and distribution filenames

`packaging.utils` turns the names, versions and filenames a Python distribution carries into
their canonical forms, and refuses the ones that are not legal.

### Behavioural clauses

C1. `canonicalize_name(name)` folds a project name to lower case and collapses any run of
    the separators `-`, `_` and `.` into a single `-`.
C2. `canonicalize_name(name, validate=True)` additionally checks the name against the core
    metadata grammar and raises `InvalidName` for anything the grammar does not admit. A
    legal name is a run of letters and digits, optionally separated by single `-`, `_` or
    `.` characters, and **nothing** may follow the final character, so any control
    character, line break or carriage return anywhere in the name makes it illegal.
C3. `is_normalized_name(name)` reports whether a name is already in the form
    `canonicalize_name` produces.
C4. `canonicalize_version(version)` returns the canonical spelling of a version, dropping
    trailing zero release segments unless `strip_trailing_zero=False` is passed. Text that
    is not a version is returned unchanged.
C5. `parse_wheel_filename` and `parse_sdist_filename` split a distribution filename into its
    canonical name, version, build tag and platform tags, and raise
    `InvalidWheelFilename` or `InvalidSdistFilename` for a filename that does not parse.

### Out of scope

- Reading files from disk, network access, and any metadata field other than the ones above.
""",
}


@dataclass
class Refusal:
    case_id: str
    reason: str
    detail: str = ""


@dataclass
class Admission:
    case_id: str
    domain: str
    impl_files: list[str]
    visible: list[str]
    reserve: list[str]
    trusted: list[str]
    impl_bytes: int
    tests_bytes: int
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Reading the pack
# --------------------------------------------------------------------------------------


def changed_source_paths(pack: Path) -> list[str]:
    diff = (pack / "pr.diff").read_text()
    return sorted({m.group(1) for m in re.finditer(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)})


def source_root(pack: Path, arm: str) -> Path:
    candidate = pack / arm / "src"
    return candidate if candidate.is_dir() else pack / arm


def module_name(root: Path, path: Path) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def package_imports(text: str, this_module: str, top: str,
                    is_package: bool = False) -> set[str]:
    """Every module of ``top`` that ``text`` imports, relative imports resolved.

    ``is_package`` matters: inside ``pkg/__init__.py`` a relative import is rooted at
    ``pkg`` itself, not at its parent, and getting that wrong silently drops half a
    package from the closure.
    """
    found: set[str] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return found
    if is_package:
        package = this_module
    else:
        package = this_module.rsplit(".", 1)[0] if "." in this_module else ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == top or alias.name.startswith(top + "."):
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package
                for _ in range(node.level - 1):
                    base = base.rsplit(".", 1)[0] if "." in base else ""
                module = f"{base}.{node.module}" if node.module else base
            else:
                module = node.module or ""
            if module == top or module.startswith(top + "."):
                found.add(module)
                for alias in node.names:
                    found.add(f"{module}.{alias.name}")
    return found


def import_closure(root: Path, top: str, seeds: list[str]) -> list[Path]:
    by_module = {module_name(root, p): p for p in (root / top).rglob("*.py")}
    kept: set[str] = set()
    queue = list(seeds)
    while queue:
        module = queue.pop()
        if module in kept:
            continue
        if module not in by_module:
            parent = module.rsplit(".", 1)[0] if "." in module else None
            if parent and parent not in kept:
                queue.append(parent)
            continue
        kept.add(module)
        parts = module.split(".")
        for index in range(1, len(parts)):
            queue.append(".".join(parts[:index]))
        path = by_module[module]
        queue.extend(
            d
            for d in package_imports(
                path.read_text(), module, top, is_package=path.name == "__init__.py"
            )
            if d not in kept
        )
    return sorted(by_module[m] for m in kept)


# --------------------------------------------------------------------------------------
# De-parametrization
# --------------------------------------------------------------------------------------


class Unsupported(Exception):
    """The module uses something this transform will not silently reinterpret."""


def _parametrize_decorators(function: ast.FunctionDef) -> list[ast.Call]:
    found = []
    for decorator in function.decorator_list:
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "parametrize"
        ):
            found.append(decorator)
    return found


def _argnames(call: ast.Call) -> list[str]:
    names = call.args[0]
    if isinstance(names, ast.Constant) and isinstance(names.value, str):
        return [part.strip() for part in names.value.split(",") if part.strip()]
    if isinstance(names, (ast.List, ast.Tuple)):
        out = []
        for element in names.elts:
            if not (isinstance(element, ast.Constant) and isinstance(element.value, str)):
                raise Unsupported("parametrize names are not plain strings")
            out.append(element.value)
        return out
    raise Unsupported("parametrize names are not a literal")


def _strip_pytest_param(node: ast.AST) -> ast.AST:
    """``pytest.param(a, b)`` becomes ``(a, b)``. A marked parameter is refused."""

    class Rewriter(ast.NodeTransformer):
        def visit_Call(self, call: ast.Call):  # noqa: N802 - ast API
            self.generic_visit(call)
            is_param = (
                (isinstance(call.func, ast.Attribute) and call.func.attr == "param")
                or (isinstance(call.func, ast.Name) and call.func.id == "param")
            )
            if not is_param:
                return call
            for keyword in call.keywords:
                if keyword.arg == "marks":
                    raise Unsupported("a parameter carries marks")
            if len(call.args) == 1:
                return call.args[0]
            return ast.Tuple(elts=list(call.args), ctx=ast.Load())

    return Rewriter().visit(node)


def deparametrize_module(source: str) -> tuple[str, list[str]]:
    """Rewrite every parametrized module-level test into one function with a loop.

    Returns the new source and the names of the module-level test functions it holds.
    A ``Test``-prefixed class is dropped, because pytest would collect its methods while
    the frozen gate counts only module-level ``def test_`` lines, and those two numbers
    have to agree. A parametrized function the transform will not reinterpret is dropped
    too; an unparametrized one is carried through untouched, fixtures and all.
    """
    tree = ast.parse(source)
    names: list[str] = []
    new_body: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            continue
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
            new_body.append(node)
            continue

        decorators = _parametrize_decorators(node)
        if not decorators:
            new_body.append(node)
            names.append(node.name)
            continue
        if any(d for d in node.decorator_list if d not in decorators):
            continue

        try:
            loops = []
            for decorator in decorators:
                if len(decorator.args) < 2:
                    raise Unsupported("parametrize without an argument list")
                argnames = _argnames(decorator)
                values = _strip_pytest_param(decorator.args[1])
                loops.append((argnames, values))
        except Unsupported:
            continue
        taken = {name for argnames, _ in loops for name in argnames}
        leftover = [a.arg for a in node.args.args if a.arg not in taken]
        if leftover:
            continue

        body = node.body
        for argnames, values in reversed(loops):
            if len(argnames) == 1:
                target: ast.expr = ast.Name(id=argnames[0], ctx=ast.Store())
            else:
                target = ast.Tuple(
                    elts=[ast.Name(id=n, ctx=ast.Store()) for n in argnames], ctx=ast.Store()
                )
            body = [ast.For(target=target, iter=values, body=body, orelse=[])]
        new_body.append(
            ast.FunctionDef(
                name=node.name,
                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[],
                                   defaults=[]),
                body=body,
                decorator_list=[],
                returns=None,
                type_params=[],
            )
        )
        names.append(node.name)

    tree.body = new_body
    ast.fix_missing_locations(tree)
    rendered = ast.unparse(tree) + "\n"
    ast.parse(rendered)
    return rendered, names


def select_functions(source: str, keep: list[str]) -> str:
    """Keep only the named module-level test functions; everything else is untouched."""
    tree = ast.parse(source)
    wanted = set(keep)
    tree.body = [
        node
        for node in tree.body
        if not (isinstance(node, ast.ClassDef) and node.name.startswith("Test"))
        and (
            not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
            or node.name in wanted
        )
    ]
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + "\n"


# --------------------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------------------


def run_modules(pack: Path, arm: str, impl_files: list[Path], impl_root: Path,
                modules: dict[str, str], extra: dict[str, str]) -> dict[str, str]:
    """Run each test module against one arm, one at a time, and collect the outcomes.

    One module at a time, so a module that will not import on its own is recorded as
    unusable instead of taking every other module down with it.
    """
    outcomes: dict[str, str] = {}
    for relative in sorted(modules):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            arm_root = source_root(pack, arm)
            for path in impl_files:
                inner = path.relative_to(impl_root)
                target = root / inner
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(arm_root / inner, target)
            for name, text in extra.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(modules[relative])
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                     "--no-header", "-rA", "--tb=no", relative],
                    cwd=str(root), capture_output=True, text=True,
                    timeout=RUN_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                continue
            output = result.stdout + result.stderr
            outcomes.update({m.group(2): m.group(1) for m in OUTCOME_RE.finditer(output)})
    return outcomes


# --------------------------------------------------------------------------------------
# Building one case
# --------------------------------------------------------------------------------------


def candidate_test_modules(pack: Path) -> list[Path]:
    return sorted(p for p in (pack / "tests").rglob("test_*.py"))


def support_files(pack: Path) -> dict[str, str]:
    """Every non-test file under ``tests``, so a module runs the way the project runs it."""
    support: dict[str, str] = {}
    for path in sorted((pack / "tests").rglob("*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(pack))
        if Path(relative).name.startswith("test_") and relative.endswith(".py"):
            continue
        try:
            support[relative] = path.read_text()
        except UnicodeDecodeError:
            continue
    return support


def shown_support(pack: Path, chosen: list[str], modules: dict[str, str]) -> dict[str, str]:
    """The support a chosen module actually imports, which must be shown to be run."""
    available = {
        str(p.relative_to(pack)): p
        for p in sorted((pack / "tests").glob("*.py"))
        if not p.name.startswith("test_")
    }
    needed: dict[str, str] = {}
    conftest = pack / "tests" / "conftest.py"
    if conftest.is_file():
        needed["tests/conftest.py"] = conftest.read_text()
    for relative in chosen:
        try:
            tree = ast.parse(modules[relative])
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                stem = name.rsplit(".", 1)[-1]
                candidate = f"tests/{stem}.py"
                if candidate in available:
                    needed[candidate] = available[candidate].read_text()
    return needed


def build_case(pack: Path, domain: str) -> Admission | Refusal:
    case_id = pack.name
    notes: list[str] = []

    changed = changed_source_paths(pack)
    if not changed:
        return Refusal(case_id, "NO_CHANGED_SOURCE")
    impl_root = source_root(pack, "before")
    relative_root = impl_root.relative_to(pack / "before")
    top = (
        Path(changed[0]).parts[len(relative_root.parts)]
        if str(relative_root) != "."
        else Path(changed[0]).parts[0]
    )

    # --- de-parametrize every candidate test module -----------------------------------
    prepared: dict[str, tuple[str, list[str]]] = {}
    dropped_classes: dict[str, int] = {}
    for path in candidate_test_modules(pack):
        relative = str(path.relative_to(pack))
        try:
            rendered, names = deparametrize_module(path.read_text())
        except (Unsupported, SyntaxError) as reason:
            notes.append(f"skipped {relative}: {reason}")
            continue
        classes = sum(
            1 for node in ast.parse(path.read_text()).body
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
        )
        if classes:
            dropped_classes[relative] = classes
        if names:
            prepared[relative] = (rendered, names)
    if not prepared:
        return Refusal(case_id, "NO_USABLE_TEST_MODULE", "; ".join(notes[:3]))

    # --- the closure the changed source and those tests need ---------------------------
    # The support files count too: a conftest that cannot import takes its whole module
    # down with it, and a collection error would read as "no test separates the arms".
    support = support_files(pack)
    base_seeds = [module_name(impl_root, pack / "before" / path) for path in changed]
    for name, text in support.items():
        base_seeds.extend(package_imports(text, "tests." + Path(name).stem, top))
    seeds = list(base_seeds)
    for relative, (rendered, _names) in prepared.items():
        seeds.extend(package_imports(rendered, "tests." + Path(relative).stem, top))
    impl_files = import_closure(impl_root, top, seeds)
    impl_bytes = sum(
        (source_root(pack, "before") / f.relative_to(impl_root)).stat().st_size
        for f in impl_files
    )
    if impl_bytes > MAX_IMPL_BYTES:
        return Refusal(case_id, "IMPLEMENTATION_TOO_LARGE_TO_SHOW",
                       f"{impl_bytes:,} bytes over the {MAX_IMPL_BYTES:,} cap")

    # --- classify every test by running both arms --------------------------------------
    modules = {relative: rendered for relative, (rendered, _n) in prepared.items()}
    before = run_modules(pack, "before", impl_files, impl_root, modules, support)
    after = run_modules(pack, "after", impl_files, impl_root, modules, support)
    if not before or not after:
        return Refusal(case_id, "SUITE_DID_NOT_RUN",
                       f"{len(before)} outcome(s) on the fixed arm, {len(after)} on the "
                       f"pre-fix arm across {len(modules)} module(s)")

    visible: dict[str, list[str]] = {}
    trusted: dict[str, list[str]] = {}
    for node_id, outcome in sorted(before.items()):
        relative, _sep, name = node_id.partition("::")
        if relative not in modules or not name.startswith("test_"):
            continue
        other = after.get(node_id)
        if outcome != "PASSED":
            continue
        if other == "PASSED":
            visible.setdefault(relative, []).append(name)
        elif other in ("FAILED", "ERROR"):
            trusted.setdefault(relative, []).append(name)

    if not trusted:
        if dropped_classes:
            total = sum(dropped_classes.values())
            return Refusal(
                case_id,
                "REPAIRED_TEST_IS_CLASS_BASED",
                f"{total} Test-prefixed class(es) were dropped because the frozen gate "
                f"counts module-level test functions only, and no module-level test "
                f"separates the arms without them",
            )
        return Refusal(case_id, "NO_TEST_SEPARATES_THE_ARMS")

    # --- the shown suite is the project's own tests for the module the fix touched -----
    # Only the modules that hold a repaired test are shown. Pulling in the project's other
    # test modules would drag their imports into the shown implementation as well, and the
    # payload would stop being about the change under review.
    chosen: list[str] = sorted(trusted)
    tests_bytes = sum(len(modules[r]) for r in chosen)
    if tests_bytes > MAX_TESTS_BYTES:
        return Refusal(case_id, "TESTS_TOO_LARGE_TO_SHOW", f"{tests_bytes:,} bytes")
    notes.append(
        f"shown suite is {', '.join(chosen)}; the pack's other test modules are not shown"
    )

    # The closure so far was seeded from every candidate module. Narrow it to what the
    # chosen modules and the changed source actually import, then confirm by running the
    # chosen modules again against that narrower tree, so nothing is shown that is not run
    # and nothing is run that is not shown.
    narrow_seeds = list(base_seeds)
    for relative in chosen:
        narrow_seeds.extend(
            package_imports(modules[relative], "tests." + Path(relative).stem, top)
        )
    impl_files = import_closure(impl_root, top, narrow_seeds)
    impl_bytes = sum(
        (source_root(pack, "before") / f.relative_to(impl_root)).stat().st_size
        for f in impl_files
    )
    if impl_bytes > MAX_IMPL_BYTES:
        return Refusal(case_id, "IMPLEMENTATION_TOO_LARGE_TO_SHOW",
                       f"{impl_bytes:,} bytes over the {MAX_IMPL_BYTES:,} cap")
    chosen_modules = {r: modules[r] for r in chosen}
    before = run_modules(pack, "before", impl_files, impl_root, chosen_modules, support)
    after = run_modules(pack, "after", impl_files, impl_root, chosen_modules, support)
    visible, trusted = {}, {}
    for node_id, outcome in sorted(before.items()):
        relative, _sep, name = node_id.partition("::")
        if relative not in chosen_modules or not name.startswith("test_"):
            continue
        other = after.get(node_id)
        if outcome != "PASSED":
            continue
        if other == "PASSED":
            visible.setdefault(relative, []).append(name)
        elif other in ("FAILED", "ERROR"):
            trusted.setdefault(relative, []).append(name)

    visible_ids = [f"{r}::{n}" for r in chosen for n in visible.get(r, [])]
    trusted_ids = [f"{r}::{n}" for r in chosen for n in trusted.get(r, [])]
    if len(trusted_ids) < MIN_TRUSTED_TESTS:
        return Refusal(case_id, "NO_TEST_SEPARATES_THE_ARMS")
    if len(visible_ids) < MIN_VISIBLE_TESTS + MIN_RESERVE_TESTS:
        return Refusal(case_id, "TOO_FEW_TESTS_GREEN_ON_BOTH_ARMS",
                       f"{len(visible_ids)} green on both")

    reserve_size = max(MIN_RESERVE_TESTS, round(len(visible_ids) / 3))
    reserve_size = min(reserve_size, len(visible_ids) - MIN_VISIBLE_TESTS)
    reserve_ids = visible_ids[-reserve_size:]
    shown_ids = visible_ids[:-reserve_size]

    # --- forbidden substrings, on the same terms as the frozen gate --------------------
    scanned = {r: modules[r] for r in chosen}
    for path in impl_files:
        scanned[str(path.relative_to(impl_root))] = path.read_text()
    hits = sorted({
        f"{name}:{word}" for name, text in scanned.items()
        for word in FORBIDDEN if word in text.lower()
    })
    if hits:
        return Refusal(case_id, "FORBIDDEN_TEXT", ", ".join(hits[:4]))
    if any(BANNER_RE.search(text) for text in scanned.values()):
        return Refusal(case_id, "SOURCE_CARRIES_A_BANNER_LINE")

    carried = shown_support(pack, chosen, modules)
    if case_id not in CONTRACTS:
        return Refusal(case_id, "NO_CONTRACT_WRITTEN",
                       "a twin without a specification is not a twin")
    _emit(pack, case_id, domain, impl_files, impl_root, modules, carried,
          chosen, shown_ids, reserve_ids, trusted_ids)
    return Admission(
        case_id=case_id,
        domain=domain,
        impl_files=[str(p.relative_to(impl_root)) for p in impl_files],
        visible=shown_ids,
        reserve=reserve_ids,
        trusted=trusted_ids,
        impl_bytes=impl_bytes,
        tests_bytes=tests_bytes,
        notes=notes,
    )


def _by_module(ids: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for node_id in ids:
        relative, _sep, name = node_id.partition("::")
        grouped.setdefault(relative, []).append(name)
    return grouped


def _emit(pack: Path, case_id: str, domain: str, impl_files: list[Path], impl_root: Path,
          modules: dict[str, str], support: dict[str, str], chosen: list[str],
          shown_ids: list[str], reserve_ids: list[str], trusted_ids: list[str]) -> None:
    target = HISTORICAL_DIR / case_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    contract = CONTRACTS[case_id].lstrip("\n").rstrip() + "\n"
    hits = sorted({w for w in FORBIDDEN if w in contract.lower()})
    if hits:
        raise SystemExit(f"{case_id}: the contract carries forbidden text: {hits}")
    (target / "contract.md").write_text(contract)
    (target / "case.json").write_text(
        json.dumps(
            {
                "domain": domain,
                "tier": "historical",
                "source_pack": str(pack.relative_to(REPO_ROOT)),
                "shown_tests": len(shown_ids),
                "reserve_tests": len(reserve_ids),
                "trusted_tests": len(trusted_ids),
            },
            indent=2,
        )
        + "\n"
    )

    for arm, side in (("before", "correct"), ("after", "incorrect")):
        arm_root = source_root(pack, arm)
        for path in impl_files:
            relative = path.relative_to(impl_root)
            # The package sits at the workspace root, because that is where its own tests
            # import it from. Nesting it under a directory would leave the tests importing
            # whatever copy the interpreter happens to find instead.
            destination = target / side / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(arm_root / relative, destination)
        for group, ids in (("tests", shown_ids), ("reserve", reserve_ids)):
            wanted = _by_module(ids)
            for relative, names in wanted.items():
                stem = Path(relative).stem
                # The reserve sits beside the suite in one workspace, so its module name has
                # to differ or pytest sees two files claiming the same import path.
                filename = f"{stem}.py" if group == "tests" else f"{stem}_more.py"
                destination = target / side / group / filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(select_functions(modules[relative], names))
            for relative, text in support.items():
                helper = target / side / group / Path(relative).name
                if not helper.exists():
                    helper.write_text(text)

    oracle_dir = target / "oracle"
    oracle_dir.mkdir()
    for relative, names in _by_module(trusted_ids).items():
        (oracle_dir / Path(relative).name).write_text(select_functions(modules[relative], names))
    for relative, text in support.items():
        helper = oracle_dir / Path(relative).name
        if not helper.exists():
            helper.write_text(text)


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------

#: Domains for the historical tier, assigned from what each upstream fix was about.
DOMAINS = {
    "attrs_frozen_error_message_001": "text_processing",
    "click_shared_default_precedence_001": "state_machine",
    "packaging_marker_extra_normalization_001": "text_processing",
    "packaging_name_validation_newline_001": "encoding",
    "rich_table_padding_width_001": "collections",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive the historical twin tier.")
    parser.add_argument("--only", default="")
    args = parser.parse_args()

    if not PACKS_DIR.is_dir():
        print(f"build_historical: no ingested packs at {PACKS_DIR}")
        return 1
    HISTORICAL_DIR.mkdir(exist_ok=True)

    packs = sorted(p for p in PACKS_DIR.iterdir() if p.is_dir() and (p / "pr.diff").is_file())
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        packs = [p for p in packs if p.name in wanted]

    admitted: list[Admission] = []
    refused: list[Refusal] = []
    print(f"Deriving the historical tier from {len(packs)} ingested pack(s)\n")
    for pack in packs:
        domain = DOMAINS.get(pack.name, "text_processing")
        outcome = build_case(pack, domain)
        if isinstance(outcome, Refusal):
            refused.append(outcome)
            print(f"  [REFUSE] {outcome.case_id}: {outcome.reason}"
                  f"{' :: ' + outcome.detail if outcome.detail else ''}")
            continue
        admitted.append(outcome)
        print(f"  [ADMIT ] {outcome.case_id} ({outcome.domain})")
        print(f"             implementation {len(outcome.impl_files)} file(s), "
              f"{outcome.impl_bytes:,} bytes")
        print(f"             visible {len(outcome.visible)}, reserve {len(outcome.reserve)}, "
              f"trusted {len(outcome.trusted)}")
        for note in outcome.notes[:3]:
            print(f"             note: {note}")

    print(f"\nAdmitted {len(admitted)}, refused {len(refused)}")
    if refused:
        print("Refusals, with the reason each pack could not be made to fit:")
        for item in refused:
            print(f"  {item.case_id}: {item.reason} {item.detail}".rstrip())
    print("build_historical: OK" if admitted else "build_historical: nothing admitted")
    return 0 if admitted else 1


if __name__ == "__main__":
    raise SystemExit(main())
