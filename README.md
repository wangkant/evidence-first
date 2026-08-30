# rigor

Two Claude Code plugins:

- **`rigor`** — three behavioral guardrails that fire at three different moments in a task.
- **`scifig`** — scientific figures, from claim to submission.

```
/plugin marketplace add wangkant/rigor
/plugin install rigor@wangkant
/plugin install scifig@wangkant
```

Or copy the skills directly — they are plain Markdown and work in any harness that reads
`SKILL.md`:

```bash
git clone https://github.com/wangkant/rigor.git /tmp/rigor
cp -r /tmp/rigor/plugins/*/skills/* ~/.claude/skills/
```

---

# rigor

Coding agents fail in three specific, repeatable ways: they **build things that already exist**,
they **add work nobody asked for**, and they **state numbers they never verified**. One guardrail
each.

| | Fires | The rule in one line | What it does *not* cover |
|---|---|---|---|
| `checking-prior-work` | **Before** the work | Before the first substantive artifact, find who already did this | Whether the result is correct |
| `executing-as-specified` | **During** the work | A specified task gets the minimal literal thing, with no injected extras | Whether the task was worth doing |
| `sourcing-claims` | **When reporting** | Every number, verdict, and external fact carries a locator you opened this turn, or it is `PENDING` | Whether the experiment should have been designed that way |

The ordering matters. `sourcing-claims` cannot save an experiment that should never have been
designed the way it was: every number can be properly sourced while the whole design
re-discovers a result published a decade ago. Only `checking-prior-work` catches that, and only
because it fires before anything is built.

## How this differs from literature-search skills

There are already good skills for **doing research** — `litreview`, `deep-research`, `deepread`,
`patent`, [deep-dive](https://github.com/kimsb2429/deep-dive-skill), Academic Researcher agents.
They fire when the user **asks for research**.

`checking-prior-work` is the inversion: it fires when the user **did not ask for research** —
when they said "just implement this" or "write me a script". A literature-review skill will
never trigger on *"add a did-you-mean to my CLI"*, and that is exactly the case where the
baseline agent made **zero lookups** and invented an unsourced threshold.

The differentiator is trigger timing, not search capability. Which is why the skill's single
most important clause is: **a task not containing the word "experiment" is not an exemption.**
"Just write me a script / add a feature / pick me a threshold" is the *highest*-risk framing,
because that is exactly where the check silently never fires.

Nearest genuine neighbours, neither of which overlaps: `zero-hallucination-coder`
(Discuss→Map→Decompose→Execute→Verify, anti-scope-creep) and
[Preflight](https://github.com/preflight-dev/preflight) (catches vague requirements before
execution).

## `checking-prior-work`

Domain-general — software, data, ops, or research. Two classes:

- **Class A, prior art** — papers, issue trackers, standards, upstream docs, changelogs.
  Search *before* designing; if prior art exists, change the design *first* rather than running
  the original plan and softening the wording afterwards. Load-bearing citations get read, not
  just cited.
- **Class B, existing resources** — in order, stopping at the first that answers: this repo and
  disk → the standard library and installed dependencies (grepped **by behaviour**, not by the
  name you expect) → the authoritative dataset, API, or spec → and only then build something
  new. **Never invent a metric an authoritative source already defines.**

It requires a `PRIOR WORK` block (SEARCHED / FOUND / NOT FOUND / **VERDICT**) before the first
substantive action. `SEARCHED: none` is not a valid value. VERDICT is the load-bearing field —
it is the sentence stating what the search changed. `NOT FOUND` is mandatory whenever the
verdict is `gap` or `build-new`, because both are claims about absence, and absence means
nothing without the query and the surface attached.

## `executing-as-specified`

When a user specifies a concrete task, they have already weighed the tradeoffs. Caveat-weighing
is *their* job, done upfront in how they phrased the request. What they didn't ask for is what
they don't want — not a gap for you to fill. Adding unrequested "thoroughness" violates the
spirit of the request, not just its letter.

The deliberate inverse also holds: if the task is genuinely underspecified, this skill does not
apply — surface the choices and align first.

## `sourcing-claims`

Every number, verdict, or factual claim must carry a locator opened **this turn**; everything
else is `PENDING`. Two kinds of locator that are not interchangeable: **measurement** (an
on-disk result file and field, answering what is true of *our* data) and **external reference**
(a URL, third-party `file:line`, or DOI, answering what is true of the world). External
references can never stand in for a measurement.

An expectation is not a result. A recollection is not a verification. Training knowledge about a
library is a hypothesis until you open the installed source. Another agent's "DONE" is a claim,
not a source.

---

# scifig

A scientific figure rarely fails because someone can't drive matplotlib. It fails because it has
no claim, because the encoding lies, or because the figure and the text disagree. So the order
is: **pin the claim → choose the encoding → draw → let the script assert the numbers → run the
checker → look at it → export.**

- A four-line figure spec (CLAIM / UNIT / MAP / SOURCE) that decides the chart type before any
  code is written.
- Chart choice by the encoding-effectiveness ladder (Cleveland & McGill 1984; Mackinlay 1986),
  not from a chart catalog.
- `scripts/figstyle.py` — journal geometry, **real** font-availability resolution (metric-
  compatible substitutes rather than a silent DejaVu fallback), CVD-safe palettes, panel labels
  in figure coordinates, export with provenance written into the file metadata.
- `scripts/figcheck.py` — eight deterministic defect classes (missing glyphs, clipped text,
  colliding ticks, type below the journal floor, rainbow colormaps, continuous mapping with no
  colorbar, legend covering data, truncated bar baseline) plus dichromacy and grayscale
  simulation.
- References on chart choice, copy-pasteable recipes, colour, journal specs (including the
  matplotlib CJK font-fallback trap), and a visual review checklist.

Both scripts self-test:

```bash
python plugins/scifig/skills/scifig/scripts/figstyle.py --selftest   # style, fonts, panel labels, export
python plugins/scifig/skills/scifig/scripts/figcheck.py demo         # deliberately broken figure; all detectors fire
```

Requires matplotlib, numpy and Pillow. No seaborn dependency — the two statistical primitives
that come up on nearly every grouped figure (`box_strip`, `jitter`) are implemented in plain
matplotlib.

---

# How these were built

Every guardrail was developed with the RED-GREEN-REFACTOR loop from Superpowers'
`writing-skills`: dispatch subagents to run pressure scenarios **without** the skill, record
their rationalizations verbatim, write rules that answer those specific rationalizations, then
re-run the same scenarios. Every row in every red-flag table is something an agent actually said
in a baseline run, not something imagined.

`checking-prior-work`'s baseline (two non-domain scenarios, under time pressure):

| Scenario | RED (no skill) | GREEN (with skill) |
|---|---|---|
| Add "did you mean" to an argparse CLI | **Zero tool calls**; answered purely from training knowledge, threshold unsourced | Six tool calls; identified `difflib` as the same function CPython uses for `NameError` suggestions, and actually ran four input cases |
| Test whether p99 tail latency is JVM GC | Zero tool calls; designed a bespoke method from first principles with a self-invented `≥50 ms` threshold | Six tool calls; cited Dean & Barroso's tail-at-scale, coordinated omission, **safepoint ≠ GC pause**, and the standard JFR approach, with sources |

Both baselines failed the same way, and that failure is the origin of the skill's central clause.

Two traps worth knowing if you test skills this way yourself:

1. Once a skill file exists in `.claude/skills/`, it enters the auto-loaded skill list for
   **every** subsequent subagent — so a "no-skill control" dispatched after writing the file is
   worthless. Any clean RED must run before the file is written.
2. Test agents given a real project write into the real tree. Use hypothetical or
   foreign-domain scenarios.

## License

MIT — see [LICENSE](LICENSE). Applies to both plugins: the skill Markdown and the scifig
scripts.
