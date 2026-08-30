---
name: sourcing-claims
description: Use when about to write or report ANY number, verdict, or factual claim — a metric like R²/AUROC/latency/delta, a "which option wins" call, a count/ratio/percentage, a confound-control figure — into a summary doc, into persistent notes, or to the user as a conclusion. ALSO for claims about the outside world — what a tool/library/API does, what a paper reported, what a file format supports, what a model was trained on. ALSO when tempted to state a result from recollection or expectation, before the producing run finished, or to repeat a number computed at an earlier pipeline stage. Trigger phrases: "what's the result", "the delta / the score", "is A or B better", "robust / tied", "how many / what fraction", "the docs say", "the official way is", "X doesn't support Y", "write it into the summary".
---

# Sourcing Claims

## Overview

**The one rule:** every number, verdict, or factual claim you write must carry a locator you
opened THIS turn. Everything else is `PENDING`.

Two kinds of locator, not interchangeable:

| | **A. Measurement** | **B. External reference** |
|---|---|---|
| Locator | on-disk result file + field | URL, or third-party `file:line`, or paper/DOI |
| Answers | "what is true of OUR data" | "what is true of the world / the tool / the field" |
| Cannot answer | anything about the outside world | **anything about our data** |

An expectation is not a result. A recollection is not a verification. Training knowledge about
a library is a **hypothesis** until you open the docs or installed source. Another agent's or
an earlier session's "DONE/verified" is a **claim**, not a source — claimed ≠ verified.
**Violating the letter of this rule violates its spirit.**

Process only — never copy specific result numbers into this file.

**When NOT to use:** pure code/plumbing with no claim attached. Strategy calls are the
advisor's. Sibling guardrails: `executing-as-specified`; `checking-prior-work` — fires EARLIER,
before the work is done, when "has someone already done this / is it already built" would change
the design. This skill cannot save a run that should never have been designed that way.

## Shared checks (every claim)

Every "no" → stop; write `PENDING` or fix the gap.

1. **Locator** — exact file+field / URL / `file:line`, opened THIS turn?
2. **No bending** — acceptable outcomes stated BEFORE looking; real value kept even when it
   contradicts my prediction, and the contradiction said out loud?
3. **Really there** — actual line(s) pasted; every cited path/URL resolves?
4. **Counting basis stated** — for any count/ratio: denominator, filter/QC stage, and dedup
   rule named? A number computed BEFORE a filter, quoted AFTER it, is a new unsourced claim —
   recompute at the current stage.

## Class A — Measurement (our data)

5. **Finished** — producing run complete: correct PID dead (capture `$!`, never hardcode) AND
   output file on disk. "Looks done" ≠ done.
6. **Alternatives open** — multiple explanations fit? List all, mark OPEN, record the
   resolving test — don't default to the flattering one.
7. **Existence ≠ magnitude** — confounds: state DIRECTION separately from MAGNITUDE; get
   magnitude from a file (matched, leak-free re-run). Winner-favoring confound uncontrolled
   ⇒ INCONCLUSIVE; disclaim it.
8. **"Reproducible" = script on disk** — only claim reproducibility if a runnable script
   exists; cite its path.

### Red flags A — STOP

| Thought | Reality |
|---|---|
| "I remember it was about X" | Recollection ≠ verification. Re-open the file this turn. |
| "The run looks about done" | Confirm PID dead AND output exists. |
| "It matches what I expected" | Outcomes first; write the real value even against yourself. |
| "I'll write it now, source it later" | Unsourced numbers become next session's "facts". PENDING. |
| "The ratio from the earlier step still holds" | Post-QC/filter, the denominator changed. Recompute. |
| "The other agent said it's verified" | Their claim is your PENDING. Open the artifact yourself. |

## Class B — External (the world)

5. **Dated and versioned** — record what you read and when; for installed code cite the LOCAL
   copy (`<pkg>/file.py:LINE`) — the installed version is what runs, not upstream.
6. **Says ≠ does** — docs/FAQs/papers state intent. Where cheap, confirm against installed
   code or a one-shot experiment; report BOTH.
7. **Producer's source before inverse transforms** — before asserting what a stored field
   means (scale, offset, orientation, units), read the upstream code that wrote it.
8. **Never substitutes for A** — B may motivate or contextualize, never stand in for a
   measurement on our data. If B and A disagree about our data, A wins; record the
   disagreement.

For "does tool X support Y?": grep the INSTALLED package — by behaviour, not only by the name
you expect. A wrong-name grep is not evidence of absence.

### Red flags B — STOP

| Thought | Reality |
|---|---|
| "That library doesn't have that function" | Grep the installed copy, by behaviour and name. |
| "The docs say so, that settles it" | Docs = intent. Installed code = what runs. Cite both. |
| "The paper reported X, so ours should be fine" | Class B says nothing about OUR data. Measure. |
| "It's general knowledge about the format" | Formats have quiet per-implementation behaviour. Spec line or test. |
| "The field is obviously in log-space / 1-based / strand-aware" | Read the producer's writing code. |
