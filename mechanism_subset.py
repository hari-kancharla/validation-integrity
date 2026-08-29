#!/usr/bin/env python3
"""The Tier M subset: 30 cases drawn by the procedure frozen in protocol_k3.md.

The draw is a pure function of the pool. Nothing here looks at a result, and nothing here
can be re-run to a different answer: the same pool and the same seed give the same 30 ids,
every time, on any machine. That is what lets the realised list be written after the pool is
built while the rule that produced it was fixed before.

The procedure, restated from the protocol so this file can be read on its own:

1. A stratum is a ``(tier, domain)`` pair. Strata are ordered ascending by ``(tier, domain)``.
2. Each stratum takes ``floor(30 * n_s / N)`` slots.
3. Remaining slots go one at a time by largest fractional remainder, ties by stratum order.
4. Every stratum is then raised to at least one slot, taking from the strata with the largest
   current allocation, ties by reverse stratum order, never reducing one below one.
5. One ``random.Random(1337)`` is walked over the strata in order, drawing
   ``sample(sorted(ids), a_s)`` from each.

No stratum ever exceeds its own size.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"
SUBSET_PATH = HERE / "mechanism_subset.json"

SEED = 1337
SUBSET_SIZE = 30


def load_pool(cases_dir: Path = CASES_DIR) -> list[dict]:
    """Every case with the two fields the draw reads, in case-id order."""
    pool = []
    for case_dir in sorted(p for p in cases_dir.iterdir() if p.is_dir()):
        meta = json.loads((case_dir / "meta.json").read_text())
        pool.append(
            {
                "case_id": case_dir.name,
                "tier": meta.get("tier", "authored"),
                "domain": meta.get("domain", "unclassified"),
            }
        )
    return pool


def pool_digest(pool: list[dict]) -> str:
    """A digest of exactly what the draw depends on, so the list can be re-derived."""
    payload = json.dumps(
        [[c["case_id"], c["tier"], c["domain"]] for c in sorted(pool, key=lambda c: c["case_id"])],
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def strata(pool: list[dict]) -> list[tuple[tuple[str, str], list[str]]]:
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for case in pool:
        grouped[(case["tier"], case["domain"])].append(case["case_id"])
    return [(key, sorted(grouped[key])) for key in sorted(grouped)]


def allocate(sizes: list[int], total: int) -> list[int]:
    """Steps 2 to 4 of the procedure. Returns one slot count per stratum, in order."""
    population = sum(sizes)
    if population == 0:
        return [0 for _ in sizes]
    total = min(total, population)

    exact = [total * size / population for size in sizes]
    counts = [min(int(value), size) for value, size in zip(exact, sizes)]

    # Step 3: hand out what is left by largest fractional remainder, ties by stratum order.
    remainders = sorted(
        range(len(sizes)), key=lambda i: (-(exact[i] - int(exact[i])), i)
    )
    left = total - sum(counts)
    cursor = 0
    while left > 0:
        progressed = False
        for index in remainders[cursor:] + remainders[:cursor]:
            if counts[index] < sizes[index]:
                counts[index] += 1
                left -= 1
                progressed = True
                if left == 0:
                    break
        if not progressed:
            break
        cursor = 0

    # Step 4: nobody is left with nothing while somebody else has more than one.
    while True:
        empty = [i for i, count in enumerate(counts) if count == 0 and sizes[i] > 0]
        if not empty:
            break
        donors = sorted(
            (i for i, count in enumerate(counts) if count > 1),
            key=lambda i: (-counts[i], -i),
        )
        if not donors:
            break
        counts[donors[0]] -= 1
        counts[empty[0]] += 1
    return counts


def draw(pool: list[dict], size: int = SUBSET_SIZE, seed: int = SEED) -> list[str]:
    """The realised subset: the case ids the frozen procedure selects from this pool."""
    groups = strata(pool)
    counts = allocate([len(ids) for _key, ids in groups], size)
    rng = random.Random(seed)
    chosen: list[str] = []
    for (_key, ids), count in zip(groups, counts):
        chosen.extend(rng.sample(sorted(ids), count))
    return sorted(chosen)


def describe(pool: list[dict], size: int = SUBSET_SIZE, seed: int = SEED) -> dict:
    groups = strata(pool)
    counts = allocate([len(ids) for _key, ids in groups], size)
    selected = draw(pool, size=size, seed=seed)
    chosen = set(selected)
    return {
        "seed": seed,
        "requested_size": size,
        "realised_size": len(selected),
        "pool_size": len(pool),
        "pool_sha256": pool_digest(pool),
        "strata": [
            {
                "tier": key[0],
                "domain": key[1],
                "size": len(ids),
                "allocated": count,
                "case_ids": [case_id for case_id in ids if case_id in chosen],
            }
            for (key, ids), count in zip(groups, counts)
        ],
        "case_ids": selected,
    }


def load_subset(path: Path = SUBSET_PATH) -> list[str]:
    if not path.is_file():
        raise SystemExit(
            f"{path} does not exist. Draw it with `python mechanism_subset.py --write` "
            f"before any mechanism-tier run."
        )
    return list(json.loads(path.read_text())["case_ids"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw or verify the Tier M subset.")
    parser.add_argument("--write", action="store_true",
                        help="write mechanism_subset.json; refuses to overwrite it")
    args = parser.parse_args()

    pool = load_pool()
    result = describe(pool)
    print(f"Pool: {result['pool_size']} case(s), digest {result['pool_sha256'][:16]}...")
    print(f"Subset: {result['realised_size']} of {result['requested_size']} requested, "
          f"seed {result['seed']}")
    print("\nStratum allocation:")
    for stratum in result["strata"]:
        print(f"  {stratum['tier']:11s} {stratum['domain']:20s} "
              f"{stratum['allocated']:2d} of {stratum['size']:2d}")
    print("\nSelected case ids:")
    for case_id in result["case_ids"]:
        print(f"  {case_id}")

    if args.write:
        if SUBSET_PATH.exists():
            existing = json.loads(SUBSET_PATH.read_text())
            same = existing.get("case_ids") == result["case_ids"]
            print(f"\n{SUBSET_PATH.name} already exists and is frozen; "
                  f"the draw {'matches' if same else 'DIFFERS FROM'} it.")
            return 0 if same else 1
        SUBSET_PATH.write_text(json.dumps(result, indent=2) + "\n")
        SUBSET_PATH.chmod(0o444)
        print(f"\nWrote and froze {SUBSET_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
