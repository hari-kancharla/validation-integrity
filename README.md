# validation-integrity

Does showing a code reviewer a change's own passing test suite make them likelier to
approve a change that is wrong?

This is the experiment built to answer it. It has never been run. No reviewer has been
called, there's no `runs/` directory and no ledger file, and the 6000-call cap is
untouched. So there are no findings about reviewers here. What there is: a corpus, five
rendered conditions, the gates that check them, and measurements of what's wrong with
the corpus itself.

## The design

When an agent writes code and also writes its tests, the tests pass. That isn't
validation — it's one author grading their own work. The question is whether a reviewer
treats it as validation anyway.

Each case is a twin: two variants of one task, one correct, one subtly wrong, each
carrying a suite that passes on its own variant. A hidden oracle holds the intended
verdict. Variant letters come from seed `1337` drawn over the sorted case list — 46 a
and 52 b — and the frozen gate redraws them on every run, so a per-case label edit
doesn't survive. A letter is a function of the whole pool, not a per-case choice.

| Condition | Shown to the reviewer |
|---|---|
| `E_NONE` | the change alone |
| `E_COUPLED` | the change and its own passing suite |
| `E_LABELSWAP` | the same bytes, under a different stated origin |
| `E_DOSE_LOW` | fewer of the coupled tests |
| `E_DOSE_HIGH` | more of them |

`E_LABELSWAP` and `E_COUPLED` differ in exactly one line — the provenance sentence — in
all 196 payload pairs. So any gap between them is about the claim, not the tests.

The dose arms aren't built for every cell. The first three conditions have 196 payloads
each, `E_DOSE_LOW` has 188 and `E_DOSE_HIGH` 182, and both gaps fall entirely on the
seven adapted twins. The expanded rung needs a reserve of further green tests written for
the same variant, and those seven have none — authoring some would mean writing tests
against someone else's workspace at a visibly different quality from the suite beside
them, which varies evidence quality at the same time as quantity and confounds the thing
H8 is for. Four of the seven also have suites too short for a third to count as a
reduction. `K3_REPORT.md` section 6 gives the reasoning; the dry run names the cells.

## Pool

98 twins. 90 authored here, 7 adapted from `benchmark_sets/integrity_pilot_v0`, 1 taken
from a documented upstream fix. `build_payloads.py` rebuilds `cases/` and `payloads/`
byte-for-byte from those sources, so neither tree has to be taken on trust. Neither external origin is verified — the upstream
commit binding is unconfirmed, and the vendored pack's own sources were never opened.

The 91 authored and historical twins span fifteen domains, unevenly filled: auth,
caching, collections, concurrency, encoding, floating point, http semantics, overflow,
resource cleanup, serialization, sorting, sql, state machines, text processing,
timezones. Three carry one or two cases. The seven adapted twins aren't sorted into
these — they carry one label of their own, `adapted_integrity`.

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q         # 195 tests over the harness
.venv/bin/python study_integrity.py   # the six frozen inputs
.venv/bin/python lint_cases.py        # runs every twin against its oracle
.venv/bin/python build_payloads.py    # rebuilds cases/ and payloads/ byte-identically
.venv/bin/python run_experiment.py --mode k3p   # power tier: E_NONE, E_COUPLED, 98 cases
.venv/bin/python run_experiment.py --mode k3m   # all five, over the 30-case subset
                                                # frozen in mechanism_subset.json
.venv/bin/python analyze.py
```

Both modes rebuild the corpus and run the four gates first, then print the plan and
stop. **Nothing is sent unless `CONFIRM_RUN=1` is in the environment**, and that is
enforced twice: the runner checks it, and `reviewer_client.py` refuses to open a socket
without it regardless of what the runner did. A test asserts that no request leaves the
process when the gate is unset. Before spending, the plan and an upper bound on cost at
list prices are printed, and a plan that would overrun the ledger is refused rather than
stopped halfway through. `--smoke` narrows a confirmed run to one case and one sample per
cell — it still spends.

If a run ever happens, the spending is the part that can't be undone, so that side is
built to fail closed. The runner checks the six frozen digests before it builds anything.
The ledger serialises charges across processes with a directory lock and atomic
replacement, and refuses negative, fractional and boolean charges. A confirmed run
freezes `plan.json`, and a resume has to match it. An `inflight.json` marker goes down
before each cell and clears only once the record is flushed — so a process that dies
after sending a call stops for inspection instead of guessing whether the reply was lost.

`lint_cases.py` is an execution gate, not a metadata check. Per case it:

- runs both visible suites against their own implementations;
- requires the oracle to pass the correct variant and fail the wrong one;
- runs each suite twice and demands identical exit status and counts;
- screens vocabulary that would leak the study;
- checks that the test count a payload claims is the count pytest collects.

### Checking the corpus against itself

```bash
.venv/bin/python tools/audit_original.py --classifier --exclude-historical
#   E_NONE 0.955, E_COUPLED 0.960, over the 97 authored and adapted cases
.venv/bin/python tools/audit_original.py --classifier
#   E_NONE 0.756, E_COUPLED 0.877, over all 98
.venv/bin/python tools/audit_original.py --static            # the raw counts
.venv/bin/python tools/validate_cases.py --contract-probes   # the four C5 probes
```

The classifier reads fourteen features that count things and interpret nothing: three
character counts, two comment counts, docstrings, the stated test count, counts of
functions, imports, asserts and `isinstance` calls, longest line, unused names, and
distinct identifiers. It fits them
leave-one-case-out, with both arms of a case always held out together. No identifiers,
no contract text, no semantics. Why that matters is under Limits.

## Layout

```
protocol.md, protocol_k2.md, protocol_k3.md   the protocols, frozen by digest
protocol_k4.md                                what they establish, and the rule
                                              that replaces their decision rule
DIGESTS.sha256                                hashes of the six frozen files
case_specs/, authored/, historical/           case sources
benchmark_sets/integrity_pilot_v0/            the vendored pack, see PROVENANCE.md
cases/, payloads/                             the built twins and rendered surface
lint_cases.py, lint_payloads*.py              the frozen gates: K1, then the K2
                                              cells, then the K3 dose rungs
run_experiment.py, analyze.py                 execution and analysis
study_integrity.py, run_evidence.py           frozen-input check, run audit
tools/                                        surface audit, case validation
gen_independent_tests.py                      the E_INDEP generator, never run
```

`gen_independent_tests.py` is why H4 and H5 are unestimable: the independent suites they
need come from a model call that was never authorised, so `E_INDEP` and
`E_INDEP_MISLABELED` have no payloads. The exclusion rule covering that is in
`protocol_k2.md`.

## What the protocols establish

K1 through K3 are labelled pre-registrations and are frozen by content digest. Both of
those are true. Neither makes them pre-registrations.

The freezing is real. All six digests verify, and `study_integrity.py` and
`run_experiment.py` fail closed on a changed, missing, duplicate or symlinked frozen
input before anything runs.

The ordering isn't. `DIGESTS.sha256` was added in `72b0b04`, after all six files it
hashes. The 14 commits carrying K1 through K3 sit inside a four-second window on
2026-08-28. Nothing in this repository is signed and there are no tags, the later work
included. `protocol.md` (`5f1da9c`) is the first commit and does precede the
gates, specs, twins, cases and payloads it governs — but `protocol_k2.md` (`4a45cb3`)
and `protocol_k3.md` (`554dfbc`) land *after* the case specifications, the twins, the
built cases, the payloads and `analyze.py`. Git records that order, not when anything
was written, and nothing here is externally registered.

**So none of the three is a binding pre-registration.** They are frozen and gated but
not registered, and for K2 and K3 the recorded order runs the wrong way. Nothing has
been collected under them, and anything collected later would be exploratory.

The decision rule they share, which `analyze.py` still applies, is:

> If `delta_fa < 0.05` and the upper bound of its 95 percent CI < 0.10, the outcome is
> NULL. Otherwise the outcome is LIVE.

That rule can't be relied on to return NULL, and which way it goes can turn on a single
case. Write D for the number of pairs that disagree across the two conditions, and drive
`analyze.py`'s own `decide()` over constructed verdict patterns at n = 98. Split D evenly
and it returns NULL up to D = 24, LIVE from D = 26. But an odd D forces a one-pair
imbalance, and the sign of that one pair decides the outcome: at D = 19, ten-to-nine
returns LIVE while nine-to-ten returns NULL. The same flip happens at 25 and at 27. So
the verdict can cross from LIVE to NULL because one case changed its mind, in either
direction, at a level of disagreement nobody has measured — no reviewer has been called.
That is a property of the rule, not a prediction about the data. `protocol_k4.md`
replaces it.

## What this pool is not clean for

Validating the twins against their contracts left nine I wouldn't use confirmatorily.
Nothing is removed — all 98 folders are intact — and the adjudication is open.

One contract is self-contradictory. `overflow_signed_minimum_negation_001` accepts
`-32768` under C1 and requires rejecting it under C3. No implementation satisfies both;
the four lines are in `cases/overflow_signed_minimum_negation_001/contract.md`.

Four turn on something the contract doesn't state. Three oracles reject a defensible
blind alternative over a representation detail — maximal prefix length
(`html_preview_composition_gap_001`), the shape of a history entry
(`state_machine_guard_before_effect_001`), which attribute records a close
(`resource_cleanup_error_suppression_001`). The fourth,
`encoding_grapheme_length_limit_001`, turns on whether two leading combining marks count
once or twice.

Three reference implementations may violate their own C5.
`serialization_nested_merge_aliasing_001` and `caching_shared_mutable_value_001` share a
deeper mapping with an input; `rate_limiter` keeps old-key events after time advances on
another key. `tools/validate_cases.py --contract-probes` runs the probes for those three
plus `encoding_grapheme_length_limit_001`, whose correct arm fails its probe too; it
prints case, letter, truth label and exit status, so a `1` is a failing probe.

The ninth is `packaging_name_validation_newline_001`, the single historical case, which
is descriptive only.

That leaves 89. For those nine, "correct" and "wrong" are readings of the contract, not
settled facts.

## Prior work

That passing tests can coexist with wrong code is already established. The new part is
the decomposition: hold the change fixed, vary only whether its own suite is shown, then
vary only what you claim about where that suite came from.

On the first contrast, the closest work is Zhan et al. on patch correctness
([ESEM 2026](https://drops.dagstuhl.de/storage/00lipics/lipics-vol394-esem2026/LIPIcs.ESEM.2026.21/LIPIcs.ESEM.2026.21.pdf)).
Their pass declaration moved neither judge — but it omitted the test code, and their
source condition showed *failing* tests, not this pairing. CodeMonitorBench
([Liao et al.](https://arxiv.org/html/2607.20852v1)) holds test source and pass status
together rather than separating them.
[Gozel](https://arxiv.org/abs/2609.00088) looks at failures on visible-test-passing
candidates and commit-first judging.

The second contrast is the weaker one. Authority effects on code judgements are already
documented by [Zhao, Esmaeili and Fard](https://arxiv.org/abs/2604.16790) and
[Moon et al.](https://arxiv.org/abs/2505.16222).
[Chae et al.](https://aclanthology.org/2026.findings-emnlp.1571/) isolate the authorship
label itself, bidirectionally and with quality matched — a cleaner result than this
design would give, though on narrative constraints rather than code.

Bug-consistent generated tests and shared generator-verifier errors are established too
([Zhao, Zhou and Cohen](https://arxiv.org/abs/2607.22883);
[Konstantinou et al.](https://arxiv.org/abs/2607.05139);
[He et al.](https://arxiv.org/abs/2610.05170)), as is overrejection of correct patches
([Jin and Chen](https://arxiv.org/abs/2603.00539)). A search through 2026-11-07 found no
paper separating both contrasts on one fixed reviewer. That search wasn't exhaustive.

## Limits

**The corpus leaks.** Fourteen features that read nothing but counts tell the wrong
variant from the right one at AUROC 0.955 across the 97 authored and adapted cases. The
wrong implementation has more full-line comments in 84 of 98 cases and fewer in none.
Its suite has more test functions in 77 and fewer in none. Test docstrings run 0 correct
against 90 wrong. Over all 98 the figure drops to 0.756, but one case does that: the
historical twin carries 62,060 characters of implementation, its two `E_NONE` payloads
are a third of all `E_NONE` text, and its two arms differ by one character.

Don't read that drop as the leak being smaller than it looks. Within-case pair ranking —
does the model put the wrong arm above the right one, inside a single case — is 0.938
over 97 and 0.934 over all 98. It barely moves while AUROC collapses. So the historical
twin breaks score comparability *between* cases; it does nothing to the separation
*inside* one.

`delta_fa` compares two conditions on the same wrong variant, so it survives this
untouched. The cross-arm numbers don't: AUROC per condition, and the H2 and H9 readings
built on it, rest on a leaky baseline. `delta_auroc` is a difference of two leaky
numbers, and some of the leak cancels — but how much depends on the case set, and over
all 98 the two conditions leak unequally, 0.756 against 0.877. "Subtly wrong" describes
what I was aiming for, not what a bag of counts needs to tell the arms apart. The surface
screen in `protocol_k4.md` exists because this corpus fails all three of its legs.

**The dose arms vary content, not just quantity.** `dose.py` keeps the first *n* tests in
source order, so `E_DOSE_LOW` drops the last ones — and sometimes that's the test that
encodes the defect.

**And the usual.** The twins are authored to isolate one mechanism; whether suites
written by real agents in real repositories move reviewers the same way is a different
question. The historical tier admitted 1 of 5 ingested packs, with four refusals recorded
in `K3_REPORT.md` section 6. Three of those are collisions with two rules in this
repository's own frozen linter — module-level test counting, which misses class-based
tests, and a forbidden-substring list that real upstream code owes nothing to — rather
than defects in the packs. Only the 935 KB implementation is genuinely out of scope. One
reviewer, an engineered corpus, a measured surface artifact. None of this estimates how often the effect happens in practice, only how big
it is under the conditions built.
