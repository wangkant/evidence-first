---
name: confirming-parameters
description: >-
  Use when a research task depends on a value that the current request did not set — a threshold,
  window, population, split, resolution, matching rule, or preprocessing choice carried over from an
  earlier round, a previous run, a sibling script, or your own notes.
---

# Confirming Inherited Parameters

## Purpose

Treat every parameter as having a source and an age. A value is settled only if the current request
set it. A value the requester chose in an earlier round, or one you measured yourself last time, is a
proposal that has not been re-examined — and because it was agreed once, nobody looks at it again.

This is what makes inherited parameters expensive. A stale window or threshold does not announce
itself; it propagates through every downstream artifact and surfaces in the run whose conclusion was
already written. The cost of naming a value is a line of text. The cost of shipping the wrong
inherited one is the study.

## Where a value came from

| Source | Status | Action |
|---|---|---|
| Set in the current request | Settled | Use it as given. Do not re-derive, audit, or qualify it. |
| Set by the requester in an earlier round | Lapsed | Not binding. Decisive parameters change between rounds. Name it, show the value, let them confirm or revise. |
| Measured or chosen by you previously | Expired | Re-derive from the live system before it supports anything. |
| Read off a sibling script, template, or default | Precedent | Nobody re-examined it there either. Treat as a proposal. |

The second row is the one most often skipped. A parameter the requester fixed three rounds ago
carries their authority but not their current intent, which is what makes it the easiest wrong value
to ship unchallenged.

## Workflow

1. Before execution, list the values the result depends on and mark where each came from.
2. Anything not set by the current request is a proposal. State it with the value you would otherwise
   use, so it can be confirmed or corrected rather than silently inherited.
3. Re-derive your own prior measurements rather than citing them. Reproducing a number from notes
   demonstrates that the notes are unchanged, not that the number still holds.
4. Ask about the parameters, not about the task. "Proceed?" and "same setup as before?" read as
   diligence while concealing the choices that determine the result, and agreement to them authorizes
   nothing specific.
5. Scale the effort to the stakes. A result that will be interpreted warrants this; a quick plot, a
   single-file edit, or a tightly specified request does not. Over-confirming returns your work to
   the requester and is its own failure.

## What survives a round and what does not

Reuse artifacts, not answers. Data already collected and code that already runs should be reused
rather than regenerated — continuity of materials is not the problem this addresses. What does not
carry across a round is a measured value, a derived limit, or a conclusion. Reuse the method; re-derive
the number.

The same applies to machine and environment state. Capacity, availability, and health readings are
observations with a timestamp, not constants, and belong in a live check rather than in a
configuration file.

## Common mistakes

| Mistake | Correction |
|---|---|
| Carrying last round's settings into a new question | Show each value and let the requester confirm it still applies |
| Citing your own earlier measurement as established | Re-derive it; reproduction of a note is not verification |
| Adopting a sibling script's threshold as the standard | Treat it as an unexamined precedent, not a decision |
| Choosing a default silently and disclosing it afterwards | Name it before it shapes the result |
| Letting an inherited value read as though it were specified | Track provenance so authorship of each choice stays visible |
| Re-examining a value the current request just fixed | Direct scrutiny at what was inherited, not at fresh instructions |
| Confirming every parameter regardless of consequence | Confirm what moves the result |

Use this skill for the values a request leaves open or carries over. Once the parameters are fixed,
execution follows the stated scope.

Related skills: `executing-as-specified` governs execution once scope is settled; `sourcing-claims`
governs what may be concluded from the result; `checking-prior-work` asks whether the question was
already answered elsewhere.
