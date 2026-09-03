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

1. Classify it as **measured**, **reported**, or **inferred**.
2. Open the supporting artifact during the current work and attach a precise locator.
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
