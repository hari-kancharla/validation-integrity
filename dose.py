#!/usr/bin/env python3
"""The dose ladder: the same suite, shown at three different sizes.

`E_DOSE_LOW`, `E_COUPLED` and `E_DOSE_HIGH` differ in one thing only, the number of green
tests the payload shows. Holding everything else fixed is the whole point, so the reduced
rung is built by **deleting** whole test functions from the full suite, line for line, and
the expanded rung by **appending** a reserve suite that was written for the same variant.
Nothing is reworded, reformatted or regenerated: every line the reduced rung shows appears
byte for byte in the full rung, and every line the full rung shows appears in the expanded
one.

Deletion is by line range taken from the parse tree, decorators included, so what is left is
an excerpt of the original file rather than a re-rendering of it.
"""

from __future__ import annotations

import ast
import math
import re

BANNER_RE = re.compile(r"^# ---- (?P<path>.+?) ----$")
TEST_FUNC_RE = re.compile(r"^def (test_\w+)\s*\(", re.MULTILINE)

#: The reduced rung shows a third of the suite, and never fewer than two tests.
LOW_FRACTION = 3
MIN_LOW_TESTS = 2
#: Below this, a third of the suite is not a reduction worth calling one.
MIN_SUITE_FOR_LOW = 4


def split_concatenated(document: str) -> dict[str, str]:
    """Banner path -> file text. The inverse of the payload concatenation."""
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


def join_concatenated(files: dict[str, str]) -> str:
    return "".join(f"# ---- {path} ----\n{text}" for path, text in files.items())


def count_tests(document: str) -> int:
    return len(TEST_FUNC_RE.findall(document))


def low_count(total: int) -> int:
    """How many tests the reduced rung shows for a suite of ``total`` tests."""
    return max(MIN_LOW_TESTS, math.ceil(total / LOW_FRACTION))


def _test_spans(text: str) -> list[tuple[str, int, int]]:
    """(name, first line, last line) for every module-level test, decorators included."""
    spans: list[tuple[str, int, int]] = []
    for node in ast.parse(text).body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        start = node.lineno
        for decorator in node.decorator_list:
            start = min(start, decorator.lineno)
        spans.append((node.name, start, node.end_lineno))
    return spans


def truncate_suite(document: str, keep: int) -> str:
    """Keep the first ``keep`` module-level tests of a concatenated suite, drop the rest.

    Whole functions go, decorators included. Imports, helpers and fixtures stay, because a
    reduced suite still has to run.
    """
    if keep < 1:
        raise ValueError("a suite must show at least one test")
    files = split_concatenated(document)
    remaining = keep
    result: dict[str, str] = {}
    for path, text in files.items():
        spans = _test_spans(text)
        take = min(remaining, len(spans))
        remaining -= take
        drop = spans[take:]
        if not drop:
            result[path] = text
            continue
        lines = text.splitlines(keepends=True)
        dropped: set[int] = set()
        for _name, start, end in drop:
            dropped.update(range(start, end + 1))
        kept = [line for number, line in enumerate(lines, start=1) if number not in dropped]
        body = "".join(kept).rstrip("\n") + "\n"
        result[path] = body
    return join_concatenated(result)


def expand_suite(document: str, reserve: str) -> str:
    """The full suite followed by its reserve, as one concatenated document."""
    files = split_concatenated(document)
    for path, text in split_concatenated(reserve).items():
        if path in files:
            raise ValueError(f"the reserve collides with the suite at {path}")
        files[path] = text
    return join_concatenated(files)
