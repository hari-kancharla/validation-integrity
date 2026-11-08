# integrity_pilot_v0 — provenance

Seven of the 98 twins in `cases/` are adapted from this pack. It is vendored here so
that `build_payloads.py` runs, and so `cases/` and `payloads/` can be rebuilt from
source rather than taken on trust.

## Where it came from

The pack was authored in a separate code-review harness, not in this repository, as a
set of paired changes to small Python workspaces: one arm whose change is correct, one
whose change is subtly wrong, and a hidden oracle that distinguishes them. The pack as
a whole was pinned at

```
73dddd920590b78415d32e55a676c2316ec0c36514f63fc0085d46a1a2bc280f
```

That digest covers the complete pack, which is larger than what is vendored here, so it
will not verify against this directory. It is recorded as the identity of the source,
not as a check on this copy.

## What was copied, and what was left out

`build_payloads.py` reads exactly four things per pair: `pair.yaml` for the contract and
the `validation_paths` list, `genuine/workspace/`, `compromised/workspace/`, and
`oracle/`. Those are what is here — 8 pairs, 55 files, 220 KB.

Left out because nothing in this repository reads them: each pair's `base/` tree,
`alternates/`, the two `pr.diff` files, and `compromised/repairs/`. Also left out are
the pack's own `manifest.yaml` and `pack.sha256`, the latter because a digest of the
full pack would fail against this subset and a failing check is worse than none.

## Seven of eight

`build_payloads.admit()` requires both workspaces to contain only Python files, plus an
oracle directory. One pair is refused:

```
invoice_tax_golden_drift_001  ->  non-Python file in genuine workspace: tests/golden/invoice.txt
```

Its defect turns on a stored golden file, so the shown change necessarily includes a
non-Python asset. The refusal is kept rather than worked around: the pair is vendored,
the gate rejects it on every build, and 7 pairs are adapted into `cases/`.

## Rebuilding

```bash
.venv/bin/python build_payloads.py
```

reproduces `cases/` and `payloads/` byte-for-byte from this pack plus `authored/` and
`historical/`. Each adapted case records its origin in `meta.json` as
`benchmark_sets/integrity_pilot_v0/<pair>`, which is why the vendor path is this one and
not a differently named directory.
