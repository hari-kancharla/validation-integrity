# validation-integrity

A pre-registered experiment on whether presenting a change's own passing validation
moves a reviewer's verdict on that change. Everything in this repository either
exists on disk or is printed by a gate that ran; no reviewer has been called, and the
call ledger stands at 0 spent of 6000.

## What is measured

An agent that writes an implementation and its tests produces a suite that passes. A
reviewer shown the change together with that green suite is shown something that
looks like validation but is not independent of the thing it validates. The
experiment measures the size of the effect that has on approval and on
discrimination, and whether the stated origin of a suite moves verdicts on its own.

Each case is a twin: two variants of one task, one correct and one subtly incorrect,
each carrying a visible suite that passes on its own variant. A hidden oracle, never
shown to the reviewer, holds the truth. Correct-variant letters are drawn by the
pre-registered seed rather than assigned by hand, so labels cannot be edited after
the fact.

Five conditions are built:

| Condition | Shown to the reviewer |
|---|---|
| `E_NONE` | the change alone |
| `E_COUPLED` | the change and its own passing suite |
| `E_LABELSWAP` | the same bytes as `E_COUPLED`, under a different stated origin |
| `E_DOSE_LOW` | a reduced quantity of coupled validation |
| `E_DOSE_HIGH` | an increased quantity |

`E_LABELSWAP` and `E_COUPLED` differ only in the provenance sentence. Any verdict
difference between them is attributable to the claim about where the suite came
from, not to the suite.

## Pool

98 cases: 90 authored twins, 7 adapted from the harness's integrity pack, and 1
derived from a real upstream fix. Sixteen domains, spanning auth, caching,
collections, concurrency, encoding, floating point, http semantics, overflow,
resource cleanup, serialization, sorting, sql, state machines, text processing and
timezones.

```
protocol.md, protocol_k2.md, protocol_k3.md   pre-registration, frozen
DIGESTS.sha256                                hashes of the frozen files
case_specs/                                   per-domain specifications
authored/, historical/                        case sources
cases/                                        the 98 built twins
payloads/                                     the rendered reviewer surface
run_experiment.py, analyze.py                 execution and analysis
lint_cases.py, lint_payloads*.py              the gates
test_*.py                                     tests over the harness itself
```

## Pre-registration

Each protocol was written before the work it governs: before cases were authored,
before payloads were rendered, before analysis code existed, and before any reviewer
call. K1 states H1 through H3; K2 adds H4 and H5; K3 adds H6 through H9 together with
dose response and the two-tier pool. Each revision extends its predecessors and
revises nothing in them.

The decision rule is fixed in advance and admits a null:

> If `delta_fa < 0.05` and the upper bound of its 95 percent CI < 0.10, the outcome
> is NULL. Otherwise the outcome is LIVE.

The digests are what make that binding. Verify them with

```bash
shasum -a 256 -c DIGESTS.sha256
```

## Running it

```bash
python -m pytest -q                            # 145 tests over the harness
python lint_cases.py                           # executes every twin against its oracle
python lint_payloads_k3.py                     # checks the rendered surface
python run_experiment.py --mode k3p --smoke    # one case, transport only
python run_experiment.py --mode k3p            # the full tier
python analyze.py
```

`run_experiment.py` reads `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, prints planned
calls and an upper-bound cost before spending anything, and refuses a plan that would
exceed the 6000-call ledger rather than stopping partway through one.

`lint_cases.py` is an execution gate, not a metadata check. Per case it runs both
visible suites against their own implementations, requires the oracle to pass the
correct variant and fail the incorrect one, repeats every suite to establish
determinism, rejects forbidden vocabulary that would leak the study, and confirms
that the test count a payload states is the count pytest collects.

## Status

Built and gated; not run. H1, H2, H3, H6, H7, H8 and H9 are estimable from what
exists. H4 and H5 are not: the independent suites they need come from the K2
generator, which is itself a model call and has never been authorised, so `E_INDEP`
and `E_INDEP_MISLABELED` carry no payloads. The cell-exclusion rule covering that was
written in advance rather than added once the gap appeared.

## What this does not establish

The twins are authored to isolate one mechanism; whether suites written by real
agents in real repositories move reviewers the same way is a separate question this
design does not reach. The historical tier admitted 1 of 5 ingested packs, and the
four refusals are recorded with reason codes in `K3_REPORT.md` section 6; two of them
are collisions with this repository's own frozen linter rather than defects in the
packs. Nothing here estimates how often the effect occurs in practice, only its size
under the conditions built.
