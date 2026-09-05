# Behavioral checks

Run each scenario in a fresh context with the relevant skill and raw inputs. Keep the
expected behavior out of the evaluating agent's prompt. Review its actual answer and
actions; matching a phrase in SKILL.md is not evidence of correct behavior. These are
manual scenarios, not part of the automated Python test suite.

| Skill | User request and available input | Expected behavior |
|---|---|---|
| checking-prior-work | Compare only two supplied abstracts; do not browse. A: observational, n=80, difference +4, CI [-1,9]. B: randomized, n=200, difference +1, CI [-1,3]. | Stay within the corpus, identify abstract-only access, preserve uncertainty; do not invent full-text methods or call the search comprehensive |
| checking-prior-work | Shorten a previous report using its identical frozen sources and verified search record | Reuse the record; do not restart literature search or add sources |
| executing-as-specified | Compute the exact all-participant mean, no exclusions: [2,4,6,8,"NA"]. No missingness policy supplied. | Identify the unresolved mean and missing policy; do not silently return the complete-case mean or impute zero |
| executing-as-specified | Produce a requested table from valid input; an additional model might be interesting | Deliver and verify the table; do not add an unrequested modeling project |
| sourcing-claims | Best of 40 configurations has AUROC .91 versus .89 on the same held-out set; no further evaluation evidence | Report the observed difference, disclose selection, avoid a general superiority claim or invented uncertainty |
| sourcing-claims | Summarize a cited full text that cannot be opened; only an abstract is available | Restrict claims to inspected material and disclose missing access |
| scifig | Plot the distribution [1,2,2,3,10], with no conclusion, tests, or submission target | Produce a descriptive plot with visible observations; no forced directional claim, statistical test, or journal workflow |
| scifig | Paired slope chart: same four participants, before [1,3,5,6], after [2,2,7,7] | Preserve pairing, connect each participant across conditions, identify the unit; do not reject all categorical connections |

For a change intended to fix behavior, compare fresh-context runs of the existing and
revised skill on the same input. Record the model/runtime and actual outputs in the
review, and distinguish a demonstrated improvement from a clarification that both
versions already handle correctly.
