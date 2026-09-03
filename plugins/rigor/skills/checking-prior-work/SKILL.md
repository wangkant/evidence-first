---
name: checking-prior-work
description: Use when formulating or starting a research question, literature review, experiment, analysis, dataset, method, metric, or novelty claim where prior evidence or existing resources could change the approach.
---

# Checking Prior Work

## Purpose

Before producing a substantive research artifact, determine what is already known and what
already exists. The check should shape the question, method, and claim—not merely decorate
the final report with citations.

Two searches are distinct and often both matter:

| Search | Typical sources | Question answered |
|---|---|---|
| Prior evidence | Primary studies, reviews, protocols, preregistrations, standards, authoritative documentation | What is already known, disputed, or constrained? |
| Existing resources | Project files, lab records, prior analyses, datasets, instruments, code, established methods | What can be reused, extended, or validated rather than recreated? |

## Workflow

1. State the proposed research question or decision in one sentence.
2. Search the most relevant internal and external sources. Use queries broad enough to find
   synonymous terms, competing methods, negative results, and earlier versions of the work.
3. Open the load-bearing sources. Titles, snippets, and remembered citations are leads, not
   evidence.
4. Compare the proposed work with what you found: replicate, extend, contrast, synthesize,
   reuse, adapt, or pursue a supported gap.
5. Revise the question, design, or originality claim before proceeding.

Search depth should match the stakes: a focused check may be enough for a small exploratory
analysis, while a novelty claim or major study needs broader coverage. It never scales to
zero when prior work could materially change the result.

## Required record

Before the first substantive deliverable, provide:

```text
PRIOR WORK
  QUESTION : <research question or decision>
  SEARCHED : <sources and literal queries>
  FOUND    : <precise locator> — <relevant finding or reusable resource>
  NOT FOUND: <bounded absence statement tied to the searched sources>
  VERDICT  : <replicate | extend | contrast | synthesize | reuse | adapt | supported gap>
             — <what changes in the proposed work>
```

`NOT FOUND` is required for a gap or originality claim. Phrase it as a bounded search result,
not proof that nothing exists.

## Common mistakes

| Mistake | Correction |
|---|---|
| Searching after the analysis is complete | Search early enough to change the design |
| Treating one database or vocabulary as exhaustive | Vary terminology and search more than one relevant surface |
| Citing a source without reading the relevant section | Open and inspect the passage, method, table, or artifact used |
| Calling an unsearched area novel | Report the search boundary and qualify the claim |
| Rebuilding a dataset, measure, or method by default | Check established and project-local resources first |

Mechanical formatting, a fully specified rerun, or a narrow correction with no research
decision does not require a new prior-work review.

Related skills: `executing-as-specified` preserves the agreed scope during the work;
`sourcing-claims` connects the final statements to evidence.
