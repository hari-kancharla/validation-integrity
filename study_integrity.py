"""Read-only verification of the existing frozen study manifest."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

FROZEN_FILES = frozenset(
    {
        "protocol.md",
        "protocol_k2.md",
        "protocol_k3.md",
        "lint_cases.py",
        "lint_payloads.py",
        "mechanism_subset.json",
    }
)
MAX_BYTES = 8 * 1024 * 1024


def _read(path: Path, limit: int) -> bytes:
    if path.is_symlink():
        raise ValueError("frozen files cannot be symlinks")
    with path.open("rb") as handle:
        content = handle.read(limit + 1)
    if len(content) > limit:
        raise ValueError("frozen file exceeds verification limit")
    return content


def verify_frozen_files(directory: Path) -> dict[str, str]:
    """Fail closed on changed, missing or ambiguous frozen inputs; never rewrite them."""
    try:
        manifest = _read(directory / "DIGESTS.sha256", 8192).decode("utf-8")
        expected = {}
        for line in manifest.splitlines():
            match = re.fullmatch(r"([a-f0-9]{64})  ([A-Za-z0-9_.-]+)", line)
            if match is None or match[2] in expected:
                raise ValueError("invalid or duplicate frozen manifest entry")
            expected[match[2]] = match[1]
        if set(expected) != FROZEN_FILES:
            raise ValueError("frozen manifest does not contain exactly the six registered files")
        actual = {
            name: hashlib.sha256(_read(directory / name, MAX_BYTES)).hexdigest()
            for name in sorted(expected)
        }
        if actual != expected:
            changed = ", ".join(name for name in actual if actual[name] != expected[name])
            raise ValueError(f"frozen artifacts changed: {changed}")
        return actual
    except (OSError, ValueError) as error:
        raise SystemExit(f"frozen study verification failed: {error}") from error


def main() -> int:
    hashes = verify_frozen_files(Path(__file__).resolve().parent)
    print(
        json.dumps(
            {
                "schema": "validation-integrity.frozen-check/1",
                "verified_files": hashes,
                "execution_performed": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
