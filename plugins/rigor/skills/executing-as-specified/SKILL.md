---
name: executing-as-specified
description: Use when carrying out a research request whose question, evidence, methods, constraints, or deliverable are already specified, especially when tempted to add unrequested analyses, filters, controls, or interpretations.
---

# Executing Research As Specified

## Purpose

Treat a defined research request as a scope contract. Preserve what was asked so the output
answers the intended question and remains comparable with related work.

This is not blind compliance. If the requested procedure would be invalid, misleading,
unsafe, unethical, impossible, or internally inconsistent, surface the problem and request or
state the smallest necessary deviation. Do not silently redesign the study.

## Scope contract

Before execution, extract only the dimensions the request actually fixes:

| Dimension | Examples |
|---|---|
| Question | Hypothesis, comparison, estimand, decision |
| Evidence | Population, corpus, samples, sources, time window |
| Method | Model, assay, coding scheme, statistical test, search protocol |
| Constraints | Inclusion/exclusion rules, thresholds, matching, budget |
| Deliverable | Table, figure, memo, dataset, notebook, concise answer |

Unspecified dimensions remain choices to resolve proportionally; they are not permission to
expand the research question.

## Workflow

1. Restate the operative scope internally or briefly in the work product.
2. Use the shortest sound path that satisfies it, reusing compatible existing materials.
3. Do not silently add or remove filters, outcomes, populations, baselines, controls,
   preprocessing, sensitivity analyses, or interpretation.
4. Resolve routine implementation choices directly. If a missing choice changes the
   estimand, population, interpretation, cost, or irreversible action, use an already
   authorized rule or ask one focused question. Disclosure alone does not authorize a
   material change to a fixed requirement. Complete unaffected work while it is unresolved.
5. If a necessary integrity check changes the requested procedure, label the change and its
   effect. Otherwise keep optional extensions separate from the requested result.
6. Report the requested deliverable first.

## Integrity checks and stopping

Checks needed to compute the requested result correctly belong to the task: validate
schema, units, join cardinality, missingness, and whether the producing run completed.
Detection does not authorize dropping rows, deduplicating entities, imputing values, or
changing thresholds. Apply the stated policy; otherwise expose the affected result as
unresolved. For example, a mean with an unspecified missing-value policy must not silently
become a complete-case mean.

Finish when the requested artifact exists, the checks needed to trust it have passed,
and material limitations are stated. Extra models, controls, or sensitivity analyses are
separate work unless requested or necessary to resolve a demonstrated validity problem.
Exploratory results remain exploratory; do not describe choices made after inspecting
results as prespecified.

## Common mistakes

| Mistake | Correction |
|---|---|
| Adding an interesting secondary analysis | Keep it separate and optional |
| Quietly applying a preferred preprocessing pipeline | Use the specified method or disclose the deviation |
| Importing assumptions from another project or earlier conversation | Treat background as context, not an unstated requirement |
| Broadening the population or evidence base for completeness | Preserve the requested boundary |
| Following a flawed instruction without warning | Surface material validity, ethics, safety, or feasibility issues |
| Turning a small request into a full research program | Deliver the scoped answer before proposing extensions |

Use this skill only when the task is sufficiently defined. If the central question, evidence,
or success criterion is genuinely ambiguous, align on those choices before execution.

Related skills: `checking-prior-work` evaluates what should be done before scope is fixed;
`sourcing-claims` verifies what can be concluded after execution.
