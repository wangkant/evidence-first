---
name: checking-prior-work
description: Use when starting substantive work — designing an experiment or analysis, implementing a feature or algorithm, defining a metric/threshold/criterion, building a dataset, choosing an approach. ALSO when about to hand-roll something that sounds standard, invent a scoring rule, or write a script from scratch. ALSO before calling anything new, novel, first, or a gap. Symptoms: reaching for a plan or code with zero lookups; the task framed as "just build/implement X" rather than "research X"; time pressure ("I need it today", "ship today"); "I already know how this works". Trigger phrases: "design an experiment", "write me a script", "just implement it", "add a feature", "define a criterion / threshold / metric", "from scratch", "novel", "first to", "no one has done this".
---

# Checking Prior Work

## Overview

**The one rule:** before producing the first substantive artifact — plan, script, job, metric —
find who already did this. **Zero lookups is a decision, and it is almost always the wrong one.**

| | **A. Prior art** | **B. Existing resources** |
|---|---|---|
| Where | papers, issue trackers, standards, upstream docs, changelogs | this repo/disk, stdlib & installed deps, authoritative datasets & official APIs, existing pipelines/tools |
| Answers | "is this question already answered?" | "is this thing already built?" |
| Cost of skipping | you rediscover a known result and call it a finding | you rebuild a worse version of what you already have |

**A search you didn't run is not an absence of prior work.** "Nothing came up" describes your
query, not the world — so it must carry the query.

**Violating the letter of this rule violates its spirit.**

## When it fires

ANY of: you are about to define a metric, threshold, or criterion; write more than ~30 lines of
new logic; launch a job costing more than ~30 minutes; produce a deliverable someone will cite,
ship, or build on; or call something new / novel / first / a gap.

Not: mechanical edits, renames, formatting; debugging one specific local failure; running a
command the user fully specified (see `executing-as-specified`).

**The task not containing the word "experiment" or "research" is not an exemption.**
"Just write me a script / add a feature / pick me a threshold" is the **highest**-risk framing —
exactly where this check silently never fires.

## Required output — the PRIOR WORK block

Produce it **before** the first substantive action. Which form is fixed by what you are producing.

**Writing a plan, pre-registration, docstring, README, or PR description** — full block, own section:

```
PRIOR WORK
  SEARCHED : <surface + the literal query>              # ≥1, always
  FOUND    : <locator: DOI/PMCID/URL/path:line/pkg.func> — <what it concluded or does>
  NOT FOUND: <what you looked for, on which surface>    # conditioned statement, not a fact
  VERDICT  : A → replicate | extend | contradict | gap
             B → reuse <locator> | adapt <locator> | build-new because <reason>
```

**Answering in chat** — same fields inline, before the deliverable. A list of links at the bottom
is not this: it has no VERDICT, so it never changed what you built.

- `SEARCHED: none` is not a value. Delete the block and go look.
- **VERDICT is load-bearing** — the sentence saying what the search changed. Never omitted.
- **NOT FOUND is required when the VERDICT is `gap` or `build-new`.** Both are claims about
  absence; absence means nothing without the query and surface attached.
- Budget scales with the work — one query for an afternoon's script, a survey for a headline
  result. It never scales to zero.

## Class A — prior art

1. **Search before designing.** The result is an *input* to the design, not a footnote on it.
2. **Prior art exists ⇒ change the design first.** Re-aim to replication, or to a question that
   isn't taken. Do not run the original plan and soften the wording afterwards.
3. **Load-bearing citations get read.** Title and abstract are not a finding — open the passage.
4. **Already ran it? Downgrade honestly.** Restate as replication; stop presenting it as new.
5. **Cheap surfaces first:** Europe PMC / OpenAlex / arXiv REST (plain `curl`), upstream issue
   trackers and changelogs, standards documents. Then WebSearch.

### Red flags A — STOP

| Thought | Reality |
|---|---|
| "This is a build task, not research" | Highest-risk framing. Metrics, thresholds and criteria all have literature. |
| "I'd know already if this were well-known" | Training recall is not a search. Run one query. |
| "I'll check the literature once I have results" | Then it can only shrink your claim; it can no longer improve the design. |
| "Searching costs more than it saves" | Five minutes against a re-aimed or discarded run. |
| "If I look, I might find it's been done" | That IS the deliverable. Finding out after you publish is the expensive version. |
| "Nothing came up, so it's novel" | Nothing came up *on that query, on that surface*. Record both. |
| "The user asked for the experiment, not a lit review" | They asked for a result that stands up. A known result doesn't. |

## Class B — existing resources

Search in this order, stop at the first that answers:

1. **Here** — grep this repo, list the results directory. Already computed? Already a function or
   pipeline for it? What is that artifact's provenance?
2. **Installed** — stdlib and installed deps, grepped **by behaviour**, not only by the name you
   expect. A wrong-name grep is not evidence of absence.
3. **Authoritative** — the official dataset, API, or spec that *defines* the quantity.
4. **Build new** — only now, and say why 1–3 didn't fit.

**Never invent a metric an authoritative source already defines.** A self-designed score is a new,
unvalidated instrument: use the real one, or validate yours against it and report the agreement.

### Red flags B — STOP

| Thought | Reality |
|---|---|
| "I'll just write a quick scoring rule / pick a threshold" | Where did that number come from? Cite it or measure it. |
| "Faster to rewrite than to find it" | You don't know the cost of finding it — you haven't looked. |
| "The library probably doesn't do that" | Grep the installed copy, by behaviour. See `sourcing-claims`. |
| "The existing artifact might be stale" | Checking its provenance is cheaper than regenerating it. |
| "I'll recompute to be safe" | A recompute is only safe if you also verify the recompute. |
| "Standard tooling won't fit our case" | Name the requirement it fails. If you can't, it fits. |

Sibling guardrails: `sourcing-claims` (fires when about to state a claim), `executing-as-specified`
(fires when the user specified exactly what to run).
