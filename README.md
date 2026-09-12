# evidence-first

Research skills that help agents check what is known, carry out the requested work,
and make claims the evidence supports. Includes tools for scientific figures.

- **`rigor`** — three research guardrails for checking prior work, staying within the
  requested scope, and grounding claims in evidence.
- **`scifig`** — scientific figures, from claim to submission.

```text
/plugin marketplace add wangkant/evidence-first
/plugin install rigor@wangkant
/plugin install scifig@wangkant
```

These are **Claude Code** plugin commands. `wangkant` is the marketplace identifier;
`evidence-first` is the repository name. The plugins remain independently installable.

The skills are plain Markdown and can also be copied into any harness that reads
`SKILL.md`:

```bash
git clone https://github.com/wangkant/evidence-first.git /tmp/evidence-first
mkdir -p ~/.claude/skills
cp -r /tmp/evidence-first/plugins/*/skills/* ~/.claude/skills/
```

For Codex, copy the same skill directories into `~/.agents/skills/` instead. Preserve
each whole directory so scifig's scripts and references travel with its entrypoint.
The Markdown research skills need no Python dependencies; scifig's helpers do.

### Try it

| Request | What the skills help with |
|---|---|
| “Check whether this question has already been answered; use only these papers.” | Inspect the permitted corpus, describe coverage, qualify a gap claim |
| “Run this analysis exactly as specified.” | Preserve filters and methods, check inputs, expose unresolved choices |
| “Does 0.91 versus 0.89 show our model is better?” | Separate the observed difference from uncertainty and evaluation leakage |
| “Show this distribution; I don't have a conclusion yet.” | Make an exploratory plot without inventing a finding or statistical test |

Use a skill by its name in your agent, or let a compatible host select it from its
description. Discovery and invocation syntax depend on the host. The skills guide agent
behavior; they do not themselves grant browsing access or enforce correctness.

---

## rigor

Research can go wrong before, during, or after the analysis: a question may repeat known
work, a setting may be inherited from an earlier round without re-examination, the execution
may drift beyond the stated scope, or the final claims may outrun the evidence. `rigor` adds
one skill at each point.

| Skill | When it applies | Core rule |
|---|---|---|
| `checking-prior-work` | Before substantive research work | Check relevant literature, records, data, methods, and prior analyses before deciding what to do |
| `confirming-parameters` | Before execution, when the request leaves a value open | Treat a setting carried over from an earlier round, a prior run, or your own notes as a proposal to confirm or re-derive, not a decision |
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

The skill keeps a concise prior-work record: what was searched, what was found, what
was not found, and how the result changes the proposed work. Search depth scales with the
claim. A small task can record this in a few sentences; an unchanged verified record can
be reused. Access failures and sources not searched are distinct from negative findings.

### `confirming-parameters`

Every parameter has a source and an age. A value set in the current request is settled. A
value the requester chose in an earlier round has lapsed: decisive settings change between
rounds, so it is shown and confirmed rather than inherited. A value you measured or chose
yourself previously has expired and is re-derived, since reproducing a number from notes shows
the notes are unchanged, not that the number still holds.

The skill asks about the parameters rather than the task, because "proceed?" and "same setup as
before?" conceal the choices that determine the result. Materials carry across rounds — data
already collected and code that already runs are reused — while measured values, derived limits,
and conclusions are re-derived. Effort scales with stakes; confirming settings that cannot change
the result returns the work to the requester for no gain.

### `executing-as-specified`

A defined research request is treated as a scope contract. The skill preserves the stated
question, population or corpus, evidence, methods, exclusions, and output. It prevents
silent additions such as extra filters, analyses, controls, or interpretations that change
the meaning of the result.

Necessary input and integrity checks belong to the task. Discovering missing values or
duplicate keys does not authorize silently dropping records. Routine choices are resolved
directly; a material change to a fixed requirement needs an authorized rule or a focused
question. Work ends once the scoped artifact and its necessary checks are complete.

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

A scientific figure needs a clear question or supported claim, a faithful encoding, and
agreement between its data and annotations.
The workflow is: **state the question or claim → choose the encoding → draw → verify the numbers → run the
checker → inspect the render → export.**

- A four-line figure spec (`QUESTION or CLAIM / UNIT / MAP / SOURCE`) that determines the chart before
  code is written.
- Chart choice guided by encoding effectiveness rather than a chart catalog.
- `scripts/figstyle.py` for journal geometry, font resolution, CVD-safe palettes, panel
  labels, and provenance-aware export.
- `scripts/figcheck.py` for deterministic defect checks plus dichromacy and grayscale
  simulation.
- References for chart choice, recipes, color, journal requirements, and visual review.

### Dependencies and checks

Python 3.10+ is required for the helpers. Install plotting dependencies with:

```bash
python -m pip install matplotlib numpy Pillow
```

PDF file inspection additionally needs `pypdf`; vector preview through `--cvd` needs
`pymupdf`. Neither is needed to audit an in-memory matplotlib Figure.

Run the style smoke test and the deliberately defective checker demo:

```bash
python plugins/scifig/skills/scifig/scripts/figstyle.py --selftest
python plugins/scifig/skills/scifig/scripts/figcheck.py demo
```

Check an exported figure:

```bash
python plugins/scifig/skills/scifig/scripts/figcheck.py figure.png --inches 3.5 2.5 --strict
```

Exit codes: `0` means no blocking finding, `1` means `FAIL` (or `WARN` with `--strict`),
and `2` means invalid CLI arguments. The demo intentionally prints defects and exits `0`.
Warnings include unsupported formats and skipped checks. File inspection covers raster
DPI and dimensions, or the first PDF page's dimensions and fonts. It does not inspect SVG
internals or establish scientific validity. Audit the Figure before export and inspect
its rendered preview as well.

## Development

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

CI runs on Python 3.10 and 3.12. Tests validate marketplace/plugin version agreement,
skill entrypoints and bundled references, real figure files, and CLI failure behavior.
See [behavioral scenarios](tests/behavioral-scenarios.md) for manual skill evaluation;
structural tests alone cannot establish that an agent follows the guidance.

## License

MIT — see [LICENSE](LICENSE). Applies to both plugins, including the skill Markdown and the
scifig scripts.
