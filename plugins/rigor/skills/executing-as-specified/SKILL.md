---
name: executing-as-specified
description: Use when the user gives a concrete run/plot/edit/build instruction and you feel the pull to ALSO add something they didn't ask for — an extra filter, edge-case or boundary handling, an extra control or baseline, a preprocessing step, validation, retry logic, defensive re-sorting — usually triggered by a remembered project concern from memory or earlier context. Symptoms: "I should also handle…", "to be safe…", "the project cares about X so…", a simple task turning complex.
---

# Executing As Specified

## Overview

When the user specifies a concrete task — "run X", "draw this chart", "edit this function" — they
have ALREADY weighed the tradeoffs and decided how they want it. **Caveat-weighing is the USER's
job, done upfront in how they phrased the request.** Do the simple, literal, minimal-path thing.

**What they didn't ask for is what they don't want — not a gap for you to fill.** Adding
unrequested "thoroughness" violates the spirit of the request, not just its letter. Simpler beats
over-cautious.

## When to Use

- The user gave a concrete execution instruction (run / plot / build / extract / edit) whose shape
  is already decided.
- You catch yourself about to add, unrequested: a filter, boundary/edge-case handling, an extra
  control or baseline, a preprocessing or dimensionality-reduction step, re-sorting, validation,
  or error-handling scaffolding.
- A task that should be a few lines is sprouting branches and comments justifying them.

**When NOT to use:** the task is genuinely coarse or underspecified (scope, target, parameters
unpinned) → opposite move: surface the choices and align FIRST. This skill is only for
ALREADY-specified execution.

## Quick Reference — the minimal path

1. Re-read the literal request. List only the steps it names.
2. Write the shortest correct path — reuse the simplest existing sibling script or skeleton, not
   the most decorated one.
3. One genuinely-important missing caveat? **Ask it in one line.** Never silently build it in.
   Otherwise ship it.

## Red Flags — STOP

| Thought | Reality |
|---|---|
| "This project cares about X, so I'll add the guard for it" | That concern is the user's to raise. They didn't → they don't want it here. |
| "To be safe I'll also handle the edge case / add a control" | Unrequested safety is scope creep. Ask, don't add. |
| "Memory / the docs say we always do Y" | Background is not a requirement injected into THIS task. Re-read the request, not the recollection. |
| "The other script does it the thorough way, I'll match it" | Match the REQUEST, not the most-elaborate sibling. |
| "It's basically the same, just more complete" | "More complete" that wasn't asked for is noise that complicates. |
| "They'll thank me for catching this" | If it were the deliverable they'd have asked. One line of question costs less than one branch of unwanted code. |

## Common Mistakes

**Dragging a remembered project concern into a plain task.** The failure shape is always the same:
a standing worry from elsewhere in the project (a data-quality caveat, a known edge case, a past
bug) gets silently compiled into a task that never mentioned it. Asked for a plain figure from an
existing pipeline, the over-built version adds a validity filter the user never raised, boundary
re-extraction for out-of-range inputs, a defensive re-sort, and provenance tracking. Same figure,
triple the complexity, none of it requested — and now the output silently differs from every
sibling figure in a way nobody documented.

**The tell:** you are writing a comment that justifies why a step is there. Requested steps don't
need justifying.

Sibling guardrails: `sourcing-claims` (fires when about to state a claim), `checking-prior-work`
(fires before the work, when "has someone already done this" would change the design).
