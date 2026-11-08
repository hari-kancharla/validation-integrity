# K1 Pilot Plan

Experiment K1: Effect of validation evidence on automated review of paired code changes.

Work strictly in phase order. Mark `[x]` only when the phase's acceptance evidence has
been printed.

- [x] **Phase 0 — Inventory and branch decision.** Explore the repository for existing
      paired correct/incorrect cases. Write `INVENTORY.md` recording what exists, exact
      paths, how visible validation and hidden oracles are represented, how to execute
      them, and the chosen branch (A = reuse >= 6 qualifying existing pairs, B = build
      the six specified cases).
- [x] **Phase 1 — Pre-registration.** Write `protocol.md` with the pre-registered title,
      hypotheses, conditions, reviewer settings, unit of analysis, primary and secondary
      metrics, verbatim decision rule, exclusions and seed. Commit it alone with the
      message `add k1 protocol`.
- [x] **Phase 2 — Build the six paired cases** (Branch B) plus `lint_cases.py` and
      `lint_payloads.py`. Commit with the message `add k1 cases and linters`. After that
      commit, `protocol.md`, `lint_cases.py` and `lint_payloads.py` are immutable.
- [x] **Phase 3 — Payloads and reviewer client.** Write `build_payloads.py` (emitting
      `payloads/<case_id>/<variant>/<condition>.md`) and `reviewer_client.py`.
- [~] **Phase 4 — Run.** Write `run_experiment.py`: build payloads, run both linters,
      enumerate and shuffle the call plan, print the planned call count and cost, stop
      unless `CONFIRM_RUN=1`, and on confirmation record `runs/<UTC>/records.jsonl` plus
      `manifest.json` with resume support.
- [x] **Phase 5 — Analysis, tests first.** Write `test_analysis.py` before `analyze.py`,
      then implement the pre-registered statistics and emit `results.md` / `results.json`.
- [ ] **Phase 6 — Commits and final report.** Commit the remaining artifacts in order and
      print the definition-of-done checklist with PASS/FAIL and evidence for each item.

## Phase status notes

- Branch A folded the Phase 2 case-authoring step into the adapter, so the cases were
  materialized by `build_payloads.py` and then gated by `lint_cases.py`. Both linters were
  written and validated in that pass.
- Phase 4 is built and its dry run is verified, but the confirmed run has not been executed:
  no reviewer credential is present in this environment and spending was not authorized.
  `CONFIRM_RUN=1` plus a provider key is all that is missing.
- Phase 5 is complete as code and tests. `analyze.py` has not been pointed at real data,
  because there is none yet and none may be invented.
- Phase 6 commits are deferred at the user's request.

## K2 upgrade

Operating rules R1-R9 remain in force. Hard call cap raised to 1500.

- [x] **Step 1 — Grow the pool to 13.** Build the six authored cases to the original
      Branch B specification and add them alongside the 7 adapted pairs. Every new case
      must pass the frozen `lint_cases.py` unchanged; if a frozen check cannot accommodate
      them, that is a blocking condition.
- [x] **Step 2 — Independent evidence.** `gen_independent_tests.py`: a generator model
      sees only `contract.md`, never an implementation, and writes 8-14 tests. Up to 5
      candidates per (case, variant); keep the first that is valid Python, passes its own
      variant, and is free of forbidden substrings. Record `INDEP_UNAVAILABLE` where none
      of the 5 works, archive every raw generation, and record cross-variant outcomes for
      the independent-test detection rate.
- [x] **Step 3 — Five conditions.** E_NONE, E_COUPLED, E_LABELSWAP, E_INDEP,
      E_INDEP_MISLABELED. Provenance sentences unchanged. Add `lint_payloads_k2.py`
      alongside the frozen payload linter.
- [x] **Step 4 — Reviewer matrix.** `REVIEWER_MODELS`, comma separated. Every record gains
      a reviewer field. 13 x 2 x 5 x 3 = 390 calls per reviewer, minus excluded cells.
- [x] **Step 5 — `protocol_k2.md` before any K2 call.** Carries H1-H3 and the decision rule
      verbatim, adds H4 and H5, states the cell-exclusion rule, reviewer list and the cap.
      Frozen once written.
- [x] **Step 6 — Analysis extensions, tests first.** Per-reviewer tables, content and label
      main effects, interaction, independent-test detection rate, evidence-citation rate.
      All 20 existing tests must still pass.
- [~] **Step 7 — Run order.** K1's 126 first, then the K2 grid one reviewer at a time,
      resumable, with a per-reviewer gate.

### K2 status notes

- Steps 1 to 6 are complete and verified. Step 7 is built and dry-run verified but not
  executed: no reviewer credential is present and spending was not authorised. Both the K1
  and K2 runs, and the generator in Step 2, stop at the money gate.
- `protocol_k2.md` was written before any K2 or generator call and is frozen alongside
  `protocol.md`, `lint_cases.py` and `lint_payloads.py`.
- `lint_payloads_k2.py` is a new companion gate; the frozen payload linter is unchanged and
  still gates the three K1 conditions.
- `call_budget.py` holds the 1500 cap in a durable ledger (`budget.json`) shared by every
  process that can spend. Each HTTP attempt is charged before it is made, so the cap binds
  across generation, both run modes, and any restart; a plan that cannot fit is refused
  before its first call. Covered by `test_call_budget.py`.

## K3 upgrade

Operating rules R1-R9 remain in force, the no-attribution rule included. Hard call cap raised
to 6000. No step below made an API call.

- [x] **Step 1 — `protocol_k3.md`, written first and then frozen.** Carries H1-H5 and the
      decision rule verbatim, adds H6 mediation, H7 acknowledgment gap, H8 dose response and
      H9 calibration, states the tiered sampling design and the Blackwell framing, and fixes
      the Tier M selection procedure. Frozen on creation; digest in `DIGESTS.md`.
- [x] **Step 2 — Recording fields.** `recording.py` widens the record to 22 fields: raw
      response, reason, response token count, latency, condition, reviewer, sample index,
      payload digest, payload size, tests shown, tier, domain and run tier. The optional
      second call per unit lives in `ReviewerClient.probe_reliance` and is confined to the
      mechanism tier; `build_reliance_messages` replays the first request and the model's own
      reply and adds one fixed sentence, and `test_recording.py` asserts that nothing else
      reaches it.
- [x] **Step 3 — Scale the pool.** 84 new authored twins across 12 domains, built from
      compact specs by `author_cases.py` and verified by execution before the frozen gate
      sees them; reserves added to the 6 K2-era authored cases; a real-defect tier derived
      by `build_historical.py` from `arena import-fix` output — a command belonging to the
      harness this study was then part of, not to this repository. 98 cases
      pass the frozen `lint_cases.py` unchanged.
- [x] **Step 4 — Tiered run design, built and dry-run, not run.** `--mode k3p` and
      `--mode k3m`, each launchable on its own, with `--reliance-probe` for the mechanism
      tier. The gate prints the call count and cost for every tier and every reviewer before
      it prints the plan for the tier selected.
- [x] **Step 5 — Analysis, tests first.** `test_analysis_k3.py` was written before any of the
      estimands and every expected number in it is worked by hand. Verdict Shift Rate, Cue
      Acknowledgment Rate, expected calibration error with a reliability table, the mediation
      decomposition, the dose-response slope, and a per-tier repeat of every primary metric.
      All previously existing tests still pass.
- [x] **Step 6 — Report.** Printed in `K3_REPORT.md`.

### K3 status notes

- Nothing has been spent. Both tiers stop at the money gate and need `CONFIRM_RUN=1` plus a
  provider key, exactly as K1 and K2 do.
- `E_INDEP` and `E_INDEP_MISLABELED` carry no payloads, because the K2 generator has never
  been run: it needs API calls that were never authorised. The K2 cell-exclusion rule covers
  this, the gate prints it, and Tier M collects the five conditions that do exist.
- The historical tier admitted 1 of the 5 ingested packs. Every refusal is recorded with its
  reason; three of them are collisions with checks in the frozen linter, which is a blocking
  condition rather than something to work around.
