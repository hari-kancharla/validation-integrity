# K3 report

Everything below is a count of something that exists on disk or a figure printed by a
gate that ran. Nothing here has been collected from a reviewer: no API call was made at
any point in this upgrade, and the call ledger stands at 0 spent of 6000.

## 1. Pool count by tier

| Tier | Cases |
|---|---:|
| `authored` | 97 |
| `historical` | 1 |
| **total** | **98** |

Every one of them passes the frozen `lint_cases.py` unchanged.

| Tier | Domain | Cases |
|---|---|---:|
| `authored` | `adapted_integrity` | 7 |
| `authored` | `auth` | 7 |
| `authored` | `caching` | 8 |
| `authored` | `collections` | 2 |
| `authored` | `concurrency` | 8 |
| `authored` | `encoding` | 7 |
| `authored` | `floating_point` | 7 |
| `authored` | `http_semantics` | 1 |
| `authored` | `overflow` | 7 |
| `authored` | `resource_cleanup` | 7 |
| `authored` | `serialization` | 7 |
| `authored` | `sorting` | 7 |
| `authored` | `sql` | 7 |
| `authored` | `state_machine` | 7 |
| `authored` | `text_processing` | 1 |
| `authored` | `timezone` | 7 |
| `historical` | `encoding` | 1 |

The authored tier is 84 twins written for K3 across the twelve domains the upgrade
names, plus the 6 authored and 7 adapted twins the pool already held. The historical
tier is 1 twin derived from a genuine upstream bug fix through the repository's own
`arena import-fix` output, a command belonging to the harness this study was then part of
rather than to this repository; the four packs that were refused are listed in section 6.

## 2. Planned calls and cost, per tier and per reviewer

Printed by the money gate before it prints the plan for whichever tier is selected.
Prices are Anthropic list prices for the default reviewer, and every figure is an upper
bound: it charges every response the full 600-token budget.

```
  tier   reviewer                     cases  calls  probe  total   input tok      cost
  k3p    claude-haiku-4-5-20251001       98   1176      0   1176     761,580     $4.29
  k3m    claude-haiku-4-5-20251001       30    876    292   1168   1,343,508     $4.85
                                                                             <= $9.14
  The probe column is the mechanism tier's second call per unit, which is
  collected only when --reliance-probe is passed.
```

With one reviewer both tiers together are 2,344 calls against the 6,000 cap. A second
reviewer would take the matrix to 4,688, which still fits; a third would not, and the
ledger would refuse the plan before its first call rather than halfway through it.

## 3. Frozen digests

```
8918931244e66df65536c350312dd6df092146cb5b898d357a9e5be491805aee  protocol.md
5f983f32a26c70ecb26e57d822184c2a1c5da9e0609d4d11fa87d010754d3ec3  lint_cases.py
696dd6e876299c0a4b9eff31cdce9c3e973417ff2ddd1d9ac0af77c8166f997e  lint_payloads.py
0b59b1713f33b4a41a371375b09c7f9e34634e0009a8c16fc1605c1d051e77a3  protocol_k2.md
ae42be19bc346f18552977dad2827915f3e94fca6fe247c929d563fcac9baeb9  protocol_k3.md
33f24786ac7d1427164f074d48ace318d45bdbbcd88116d2e5e37d1d2d7a28c7  mechanism_subset.json
```

`mechanism_subset.json` names 30 cases drawn by the frozen
procedure from a pool whose digest is `28e310d26dff0d6f2865bf52c4419996cc0782b1e381860472546f5b91d29025`.
Re-derive it with `.venv/bin/python mechanism_subset.py`, which prints the same list or says the
pool has moved.

## 4. Test count

| File | Tests |
|---|---:|
| `test_analysis.py` | 36 |
| `test_analysis_k3.py` | 37 |
| `test_call_budget.py` | 13 |
| `test_dose.py` | 18 |
| `test_mechanism_subset.py` | 19 |
| `test_recording.py` | 22 |
| **total** | **145** |

All 145 pass. Three further files were added after this report — `test_budget_safety.py`,
`test_run_evidence.py` and `test_study_integrity.py`, 50 tests between them — so the
current total is 195, which is what `pytest` collects today. The 36 in `test_analysis.py`
are the K1 and K2 tests, unchanged and still
passing; the other 109 are new. Every expected number in `test_analysis_k3.py` is worked
by hand in a comment above the assertion.

## 5. Commands to launch each tier, when authorised

Each tier is a separate run, so spending can be staged: Tier P can be collected, read and
paid for before Tier M is authorised, and either can be re-run on its own. Both refuse to
open a socket without `CONFIRM_RUN=1`, and both charge the shared ledger before each attempt.

Dry run first, which is the default and costs nothing:

```bash
.venv/bin/python run_experiment.py --mode k3p
```

Tier P, power. Every case, both variants, `E_NONE` and `E_COUPLED`, 3 samples:

```bash
CONFIRM_RUN=1 ANTHROPIC_API_KEY=... REVIEWER_MODELS=claude-haiku-4-5-20251001 .venv/bin/python run_experiment.py --mode k3p
```

Tier M, mechanism. The 30 frozen cases, every condition that has a payload, 3 samples:

```bash
CONFIRM_RUN=1 ANTHROPIC_API_KEY=... REVIEWER_MODELS=claude-haiku-4-5-20251001 .venv/bin/python run_experiment.py --mode k3m
```

Tier M with the reliance probe, which adds one further call on the first sample of each unit:

```bash
CONFIRM_RUN=1 ANTHROPIC_API_KEY=... REVIEWER_MODELS=claude-haiku-4-5-20251001 .venv/bin/python run_experiment.py --mode k3m --reliance-probe
```

A bounded transport check against one case, one sample per cell, writing to a run directory
the analysis ignores:

```bash
CONFIRM_RUN=1 ANTHROPIC_API_KEY=... .venv/bin/python run_experiment.py --mode k3p --smoke
```

Analysis of whatever has been collected, and the ledger:

```bash
.venv/bin/python analyze.py
```

```bash
.venv/bin/python call_budget.py
```

## 6. What did not fit, and why

Four things are missing or refused. None of them was worked around.

**`E_INDEP` and `E_INDEP_MISLABELED` carry no payloads.** The independent suites come from
the K2 generator, which is a model call, and no generator run has ever been authorised. The
K2 cell-exclusion rule already covers exactly this case, the gate prints the two conditions
as unavailable before it prints the plan, and Tier M collects the five conditions that do
exist. H4 and H5 cannot be estimated until the generator has run; H1, H2, H3, H6, H7, H8 and
H9 can.

**The historical tier admitted 1 of the 5 ingested packs.** Each refusal is recorded by
`build_historical.py` with the reason it could not be made to fit:

| Pack | Refusal |
|---|---|
| `packaging_name_validation_newline_001` | **admitted** — 8 modules, 61,789 bytes shown; 5 visible tests, 3 reserve, 1 trusted |
| `attrs_frozen_error_message_001` | `REPAIRED_TEST_IS_CLASS_BASED` — the tests the fix repaired are methods of `Test`-prefixed classes, and the frozen gate counts module-level `def test_` lines |
| `packaging_marker_extra_normalization_001` | `TOO_FEW_TESTS_GREEN_ON_BOTH_ARMS` — same cause: once class-based tests are dropped, one module-level test is left |
| `click_shared_default_precedence_001` | `FORBIDDEN_TEXT` — `click/core.py` uses the words `hidden` and `condition` in their ordinary senses, and both are on the frozen linter's forbidden list |
| `rich_table_padding_width_001` | `IMPLEMENTATION_TOO_LARGE_TO_SHOW` — 935,325 bytes, against a 400,000-byte cap on what a payload can show in full |

Three of these are collisions with two rules in the frozen gate rather than problems with
the packs. The
forbidden-substring list and the module-level test-count check were written for authored
twins, where those words would leak the study and where a suite has no reason to use classes;
real upstream code owes them nothing. Under the rule that frozen files stay frozen, that is a
blocking condition and it is recorded as one. Lifting it would need a K4 protocol that either
supersedes the frozen linter or restates the historical tier's admission rule.

**14 cells carry no `E_DOSE_HIGH` and 8 carry no `E_DOSE_LOW`.** The expanded rung needs a
reserve of further green tests written for the same variant, and the seven twins adapted from
`benchmark_sets/integrity_pilot_v0` have none: writing one would mean authoring tests against
someone else's workspace at a visibly different quality from the suite beside it, which would
vary evidence quality at the same time as evidence quantity and confound the very thing H8
measures. `DOSE_UNAVAILABLE` is recorded instead, and the reduced rung is skipped for the
eight cells whose own suite is too short for a third of it to be a reduction. Two of the
thirty Tier M cases are affected; they contribute the rungs they carry.

**The realised Tier M subset was written after the pool was built.** `protocol_k3.md` fixes
the selection *procedure* and was frozen before a single K3 twin existed; the list is that
procedure's mechanical output over the finished pool, written to `mechanism_subset.json` and
frozen before any mechanism-tier call. Anyone can re-derive it from the frozen pool. This is
the one place where the pre-registration is of a rule rather than of a value, and it is
recorded here rather than glossed.

## 7. What one Tier M record now holds

```
reviewer  case_id  variant  truth  tier  domain  run_tier  condition  sample_idx
status  response_raw  suspicion  verdict  reason
response_tokens  response_chars  latency_ms
payload_sha256  payload_chars  tests_shown
reliance  ts
```

The reliance probe is the only second call, it is permitted in the mechanism tier only, and
it fires on `sample_idx` 0 alone. It replays the byte-identical first request, then the
reviewer's own reply, then one fixed sentence that names no case, no condition, no test and
no part of the study. `ReviewerClient.probe_reliance` raises rather than sends if the
messages carry anything else, and `test_recording.py` reconstructs them and asserts it.
