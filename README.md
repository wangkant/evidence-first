# evidence-first

General-purpose research skills for evidence-grounded work, plus a toolkit for
publication-quality scientific figures.

- **`rigor`** — three research guardrails for checking prior work, staying within the
  requested scope, and grounding claims in evidence.
- **`scifig`** — scientific figures, from claim to submission.

```text
/plugin marketplace add wangkant/evidence-first
/plugin install rigor@wangkant
/plugin install scifig@wangkant
```

The skills are plain Markdown and can also be copied into any harness that reads
`SKILL.md`:

```bash
git clone https://github.com/wangkant/evidence-first.git /tmp/evidence-first
cp -r /tmp/evidence-first/plugins/*/skills/* ~/.claude/skills/
```

---

## rigor

Research can go wrong before, during, or after the analysis: a question may repeat known
work, the execution may drift beyond the stated scope, or the final claims may outrun the
evidence. `rigor` adds one skill at each point.

| Skill | When it applies | Core rule |
|---|---|---|
| `checking-prior-work` | Before substantive research work | Check relevant literature, records, data, methods, and prior analyses before deciding what to do |
| `executing-as-specified` | While carrying out a defined research request | Preserve the requested question, evidence, method, constraints, and deliverable; surface material problems instead of silently changing scope |
| `sourcing-claims` | When reporting findings | Distinguish measured, reported, and inferred claims, and attach a precise locator to each substantive claim |

The skills are domain-general. They apply to literature reviews, experimental and
observational studies, quantitative analysis, qualitative synthesis, benchmarking, dataset
construction, methods development, and research writing.

### `checking-prior-work`

Search two complementary surfaces before committing to an approach:

- **Prior evidence:** papers, reviews, protocols, preregistrations, standards, and other
  sources that may already answer the question or constrain the design.
- **Existing resources:** internal notes, previous analyses, datasets, instruments, code,
  and established methods that may already provide what the task needs.

The skill ends with a concise `PRIOR WORK` record: what was searched, what was found, what
was not found, and how the result changes the proposed work. Search depth scales with the
claim, but never to zero when originality, method choice, or evidence quality is at stake.

### `executing-as-specified`

A defined research request is treated as a scope contract. The skill preserves the stated
question, population or corpus, evidence, methods, exclusions, and output. It prevents
silent additions such as extra filters, analyses, controls, or interpretations that change
the meaning of the result.

Material validity, safety, feasibility, or ethics problems are still surfaced. The skill
does not require blind execution; it requires making necessary deviations explicit rather
than quietly rewriting the study.

### `sourcing-claims`

Claims are labeled by how they are known:

- **Measured:** computed or observed in the current work, with a data/result locator.
- **Reported:** stated by an external source, with a precise citation.
- **Inferred:** an interpretation that connects evidence to a conclusion, labeled as such.

Counts name their denominator and filtering stage; mutable sources record a version or
access date; conflicting evidence and unresolved uncertainty remain visible. A citation to
the literature cannot substitute for a measurement on the current data, and a local result
cannot establish a general fact about the world.

---

## scifig

A scientific figure rarely fails because someone cannot drive matplotlib. It fails because
it has no claim, because the encoding misleads, or because the figure and the text disagree.
The workflow is: **pin the claim → choose the encoding → draw → assert the numbers → run the
checker → inspect the render → export.**

- A four-line figure spec (`CLAIM / UNIT / MAP / SOURCE`) that determines the chart before
  code is written.
- Chart choice guided by encoding effectiveness rather than a chart catalog.
- `scripts/figstyle.py` for journal geometry, font resolution, CVD-safe palettes, panel
  labels, and provenance-aware export.
- `scripts/figcheck.py` for deterministic defect checks plus dichromacy and grayscale
  simulation.
- References for chart choice, recipes, color, journal requirements, and visual review.

Both scripts self-test:

```bash
python plugins/scifig/skills/scifig/scripts/figstyle.py --selftest
python plugins/scifig/skills/scifig/scripts/figcheck.py demo
```

Requires matplotlib, numpy, and Pillow.

## Development

The skills are written as small, independently triggered research behaviors. Their
instructions emphasize observable evidence, explicit scope, and qualified conclusions so
they remain useful across disciplines and research methods.

## License

MIT — see [LICENSE](LICENSE). Applies to both plugins, including the skill Markdown and the
scifig scripts.
