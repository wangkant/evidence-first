---
name: sourcing-claims
description: Use when writing a research claim, quantitative result, comparison, literature synthesis, method statement, or conclusion that must be traceable to data or external evidence.
---

# Sourcing Research Claims

## Purpose

Make each substantive claim traceable to the evidence that supports it. Distinguish what the
current work measured, what another source reported, and what the researcher inferred.

| Claim type | Appropriate locator | What it supports |
|---|---|---|
| Measured | Data/result file plus table, field, query, figure, or analysis step | A statement about the current study or dataset |
| Reported | DOI or stable URL plus page, section, table, figure, or quoted passage | What an external source states or demonstrates |
| Inferred | The supporting measured/reported evidence plus explicit reasoning | An interpretation, explanation, or synthesis |

These are not interchangeable. Literature cannot substitute for a measurement on the current
data, and a local result cannot by itself establish a general fact.

## Workflow

For every important number, comparison, method statement, or conclusion:

1. Classify it as **measured**, **reported**, or **inferred** internally; make the distinction
   clear in prose without forcing a label onto every sentence. A user-supplied value is
   reported until independently checked.
2. Inspect the supporting artifact or source material already present in context and
   attach a precise locator. Reuse a verified unchanged source; reopen it when its version,
   relevant passage, or applicability is uncertain.
3. Check that the source supports the exact scope and strength of the wording.
4. For counts, ratios, or percentages, state the denominator, unit, filters, deduplication, and
   analysis stage.
5. For mutable sources, record the version or access date. For methods, identify the version
   and parameters that affect the result.
6. Separate observation from explanation. If several explanations fit, retain the alternatives
   and name the evidence that could distinguish them.
7. If support is incomplete, qualify the statement or mark it `PENDING` rather than filling the
   gap from memory or expectation.

## Evidence checks

- Confirm the producing analysis completed and the cited output exists.
- Recompute values after material filtering or quality-control changes.
- Prefer primary evidence for load-bearing claims; use reviews for context and discovery.
- Cite the relevant passage or result, not merely a paper title or homepage.
- Represent conflicting evidence and uncertainty instead of selecting only the convenient
  source.
- Claim reproducibility only when the necessary data, code, notebook, protocol, or procedural
  detail is actually available.

## Match the conclusion to the design

A numerical lead is a descriptive result, not automatically evidence of a reliable or
generalizable improvement. Check whether comparisons use the same samples, metric,
evaluation protocol, and selection stage. If many variants were selected on the reported
test set, state that selection; it is not an untouched final evaluation.

State available uncertainty and the independent sampling unit. Do not invent confidence
intervals from summary scores, treat repeated measurements as independent replicates, or
turn a nonsignificant result into evidence of equivalence. Causal language requires a
design and assumptions that support it. If the current evidence cannot settle the claim,
give the strongest supported statement and identify the specific missing evidence.

For a supplied abstract or excerpt, cite it as such. An inaccessible full text or a search
snippet cannot support claims about unobserved methods or results. A draft may mark an
unresolved claim `PENDING`; a finished answer should omit it or state the limitation plainly.

## Common mistakes

| Mistake | Correction |
|---|---|
| Repeating a remembered result | Reopen the source or mark it `PENDING` |
| Reporting a value from an earlier pipeline stage | Recompute for the final analysis set |
| Treating correlation or association as mechanism | Label the inference and its alternatives |
| Using an external benchmark as evidence about the current data | Measure the current data directly |
| Citing documentation for what a tool actually produced | Cite both intended behavior and the observed output when both matter |
| Hiding uncertainty behind a categorical verdict | Report the uncertainty, sensitivity, or unresolved evidence |

Pure formatting or plumbing with no factual or interpretive claim does not require claim-level
sourcing.

Related skills: `checking-prior-work` shapes the study using existing knowledge;
`executing-as-specified` keeps the analysis aligned with the agreed scope.
