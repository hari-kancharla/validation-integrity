#!/usr/bin/env python3
"""One durable call ledger shared by every process that can spend money.

The per-process cap in each entry point only ever saw its own invocation, so generation,
the K1 run and each K2 reviewer could each stay under the cap while together going well
past it. This module holds the count in a file instead, so the cap binds across invocations,
across modes, and across restarts.

Two guarantees:

- **Nothing is spent past the cap.** Every HTTP attempt is charged *before* it is made, and
  the charge is persisted before the call goes out. A process killed mid-run cannot lose
  calls it already made, so a resumed run starts from the true total rather than zero.
- **A plan that cannot fit is refused up front.** ``check_plan`` compares what an
  invocation intends to spend against what is left, so a run that would breach the cap
  stops before its first call rather than halfway through.

Only real calls are charged. A dry run touches nothing.
"""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER_PATH = HERE / "budget.json"

#: Raised for K3 by protocol_k3.md. The ledger is shared, so this binds across every
#: process that can spend: generation, both K2 run modes, and both K3 run tiers.
HARD_CAP = 6000


class BudgetExhausted(RuntimeError):
    """Raised instead of making a call that would take the total past the cap."""


class CallBudget:
    def __init__(self, path: Path = LEDGER_PATH, cap: int = HARD_CAP) -> None:
        if type(cap) is not int or cap <= 0:
            raise ValueError("call cap must be a positive integer")
        self.path = path
        self.cap = cap

    # -- state -------------------------------------------------------------------------

    def load(self) -> dict:
        if self.path.is_symlink():
            raise SystemExit("Refusing to spend against a symlinked ledger.")
        if not self.path.is_file():
            if self.path.exists():
                raise SystemExit("Call ledger must be a regular JSON file.")
            return {"cap": self.cap, "spent": 0, "invocations": []}
        try:
            ledger = json.loads(self.path.read_text(), object_pairs_hook=_unique_keys)
        except (ValueError, UnicodeError) as error:
            raise SystemExit(
                "Call ledger is not readable, unambiguous JSON. Refusing to spend; "
                "inspect and recover it before continuing."
            ) from error
        if (
            not isinstance(ledger, dict)
            or type(ledger.get("cap")) is not int
            or ledger["cap"] <= 0
            or type(ledger.get("spent")) is not int
            or ledger["spent"] < 0
            or not isinstance(ledger.get("invocations"), list)
            or any(not isinstance(entry, dict) for entry in ledger["invocations"])
        ):
            raise SystemExit("Call ledger has invalid accounting fields; refusing to spend.")
        return ledger

    @contextmanager
    def _locked(self):
        # Lock the stable parent directory: atomic replacement changes the ledger's
        # inode. A lock on that replaced file would not serialize later writers.
        # The lock leaves no sidecar behind and the OS releases it on process exit.
        try:
            import fcntl
        except ImportError as error:
            raise SystemExit(
                "Spending requires POSIX file locking on a local filesystem."
            ) from error
        descriptor = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            os.close(descriptor)

    def _store(self, ledger: dict) -> None:
        """Write through a temporary file so a crash cannot leave a half-written ledger."""
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", dir=self.path.parent, prefix=".budget-", suffix=".tmp", delete=False
            ) as handle:
                temporary = Path(handle.name)
                json.dump(ledger, handle, indent=2, allow_nan=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def spent(self) -> int:
        return int(self.load()["spent"])

    def remaining(self) -> int:
        return max(0, self.cap - self.spent())

    # -- gates -------------------------------------------------------------------------

    def check_plan(self, planned: int, label: str) -> tuple[bool, str]:
        if type(planned) is not int or planned < 0:
            raise ValueError("planned calls must be a non-negative integer")
        spent = self.spent()
        remaining = max(0, self.cap - spent)
        if planned > remaining:
            return False, (
                f"{label} plans {planned} call(s) but only {remaining} remain of the "
                f"{self.cap} cap ({spent} already spent across earlier invocations)"
            )
        return True, (
            f"{label} plans {planned} call(s); {spent} spent, {remaining} remain of {self.cap}"
        )

    def charge(self, count: int = 1, label: str = "") -> int:
        """Persist ``count`` calls before they are made. Raises once the cap is reached."""
        if type(count) is not int or count <= 0:
            raise ValueError("charged calls must be a positive integer")
        with self._locked():
            ledger = self.load()
            spent = ledger["spent"]
            if spent + count > self.cap:
                raise BudgetExhausted(
                    f"call cap of {self.cap} reached: {spent} already spent, "
                    f"{label or 'this call'} would take it to {spent + count}"
                )
            ledger["spent"] = spent + count
            ledger["cap"] = self.cap
            self._store(ledger)
            return ledger["spent"]

    def note(self, label: str, **fields) -> None:
        """Append a record of one invocation, for the audit trail."""
        with self._locked():
            ledger = self.load()
            entry = {"label": label, "at": datetime.now(timezone.utc).isoformat()}
            entry.update(fields)
            ledger["invocations"].append(entry)
            self._store(ledger)

    # -- reporting ---------------------------------------------------------------------

    def describe(self) -> str:
        spent = self.spent()
        return f"{spent} spent, {self.cap - spent} remaining of {self.cap}"


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate ledger field")
        result[key] = value
    return result


def main() -> int:
    budget = CallBudget()
    ledger = budget.load()
    print(f"Call ledger: {budget.path}")
    print(f"  cap:       {ledger['cap']}")
    print(f"  spent:     {ledger['spent']}")
    print(f"  remaining: {budget.remaining()}")
    if ledger["invocations"]:
        print("  invocations:")
        for entry in ledger["invocations"]:
            extras = " ".join(f"{k}={v}" for k, v in entry.items() if k not in ("label", "at"))
            print(f"    {entry['at']}  {entry['label']}  {extras}")
    else:
        print("  invocations: none recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
