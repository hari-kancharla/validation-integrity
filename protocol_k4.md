# K4: what the earlier protocols establish, and the rule that replaces theirs

This revision does not add conditions, cases or hypotheses. It records what K1 through
K3 do and do not establish, replaces their decision rule, and fixes the screen a
rebuilt corpus would have to pass.

## Status of K1 through K3

`protocol.md`, `protocol_k2.md` and `protocol_k3.md` are labelled pre-registrations and
are frozen by content digest. Both parts of that are true and neither carries the
weight the label implies.

The freezing is real and enforced. All six entries in `DIGESTS.sha256` verify, and
`study_integrity.py` and `run_experiment.py` fail closed on a changed, missing,
duplicate or symlinked frozen input before anything is built, gated or called.

The ordering does not support the label. `DIGESTS.sha256` was added in `72b0b04`,
after each of the six files it hashes. All 14 pre-K4 commits carry author and commit
timestamps inside a four-second window on 2026-08-28, none is signed, and there are no
tags. On that record `protocol.md` (`5f1da9c`) is the first commit and precedes the
gates, specifications, source twins, cases and payloads it governs, while
`protocol_k2.md` (`4a45cb3`) and `protocol_k3.md` (`554dfbc`) follow the case
specifications, the source twins, the built cases, the payloads and `analyze.py`.

Git records that ancestry, not authoring times. A digest recorded in the same pass as
its subject fixes bytes from that commit forward and establishes nothing about when
anything was written. None of the three is externally registered; there is no timestamp
receipt and no signed tag.

So: none of the three is a binding pre-registration. They are frozen and gated but not
externally registered, and for K2 and K3 the recorded order is inconsistent with one.
Nothing has been collected under them. Anything collected under them later is
exploratory, and public registration completed before the first call is what would make
a later run confirmatory.

## The decision rule

K1 through K3 decide as follows, and `analyze.py` still applies it:

> If `delta_fa < 0.05` and the upper bound of its 95 percent CI < 0.10, the outcome is
> NULL. Otherwise the outcome is LIVE.

This does not reliably admit a null, and the outcome can turn on a single case.
`delta_fa` is a paired difference of proportions over cases, and `analyze.py` takes its
interval from a nearest-rank case bootstrap rather than a closed form. Writing D for the
number of pairs discordant between the two conditions and driving `decide()` over
constructed verdict patterns at n = 98: an evenly split D returns NULL up to D = 24 and
LIVE from D = 26, but an odd D forces a one-pair imbalance whose sign decides the
outcome. At D = 19, ten against nine returns LIVE and nine against ten returns NULL; the
same inversion occurs at D = 25 and D = 27. A verdict that moves between LIVE and NULL on
one case reversing, in either direction, is not a decision rule. How much reviewer
disagreement to expect is unknown, because no reviewer has been called; this is a
property of the rule.

It is replaced by ordered outcomes with a meaningful-effect margin of 0.10 absolute
approval probability, evaluated in order:

1. **HARMFUL** — wrong approval rises, Holm-adjusted p < 0.05.
2. **BENEFICIAL** — wrong approval falls, adjusted p < 0.05, and the 95 percent
   discrimination-change lower bound is strictly above −0.10. Otherwise **NONSPECIFIC**.
3. **NEGLIGIBLE** — otherwise, if the 90 percent interval lies strictly inside
   (−0.10, 0.10).
4. **INCONCLUSIVE** — otherwise, including unestimable contrasts.

NONSPECIFIC means the specificity criterion was not established, not that everything is
rejected. NEGLIGIBLE is interval-based equivalence at alpha .05, not a zero effect — a
90 percent interval is the two-one-sided-tests form of that. Holm controls the two
zero-effect families named above, the approval contrasts and the discrimination
contrasts, and nothing else. Report estimates and intervals alongside every label.

No code applies this rule yet. `analyze.py` still implements the rule above, which is
what `README.md` reports.

## The surface screen

`tools/audit_original.py --classifier --exclude-historical` measures what a bag of
fourteen count-only features recovers from the rendered payloads. On the current corpus
it recovers the incorrect arm at AUROC 0.955 over the 97 authored and adapted cases;
without the flag the figure over all 98 is 0.756. That is a property
of how these twins were written, and it contaminates every cross-arm estimand.

Any rebuilt or extended corpus intended for confirmatory use must, per condition, reach
AUROC <= 0.60, an upper 95 percent case-bootstrap bound <= 0.70, and
max(AUC, 1 − AUC) <= 0.65 for every single feature. Accuracy and within-case ranking are
reported alongside. The thresholds do not move, and reaching them by padding, writing
tautological tests or inventing comments would defeat the screen. Passing is a measured
screen against these fourteen features, not the absence of every confound.

## What this document does not do

It adopts no collection plan, authorises no spending, and does not approve building new
stimuli. The corpus limitations a reader needs are in `README.md`, under "What this pool
is not clean for" and "Limits", with the commands that reproduce them.
