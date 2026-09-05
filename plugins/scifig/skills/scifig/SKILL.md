---
name: scifig
description: >-
  Use when creating, revising, or checking static scientific data figures, including
  exploratory plots, statistical comparisons, heatmaps, and publication exports.
  Covers chart choice, uncertainty, accessible encoding, and figure validation.
  Not for diagrams, architecture drawings, or interactive dashboards.
---

# scifig — scientific figures, from claim to submission

## What this skill is for

A scientific figure rarely fails because someone can't drive matplotlib. It fails for one
of three reasons:

1. **The figure has no purpose** — neither a research question nor an evidence-supported
   finding guides what the reader should inspect;
2. **The encoding lies** — bars starting at 9.8, a rainbow colormap inventing boundaries,
   n=4 hidden behind a mean bar;
3. **The figure and the data disagree** — the text says 0.97, the figure says 0.94, and
   nobody notices.

So the order here is: **state the question or supported claim → choose the encoding → draw → verify
the numbers → run the checker → look at it → export.** The plotting code is the middle
step; the value is at both ends.

Not for schematics, flowcharts, or architecture diagrams. Interactive charts for web pages
or dashboards belong to a dataviz skill, not this one.

---

## Step 1: write a four-line figure spec

Before drawing, put these four lines in the plotting script's top docstring:

```
QUESTION: how does response differ between treated and matched control regions?
UNIT:     one row = one region; retain pairing IDs and report n after exclusions
MAP:      x=group, y=response, point=region; show paired differences if pairing is valid
SOURCE:   results/marks_summary.parquet, columns group, region_id, pair_id, response
```

Why each line earns its place:

- **QUESTION or CLAIM** determines the chart type. From identical data, "A is higher than B" becomes a
  grouped dot plot, "A rises with dose" becomes a line, "A correlates with B" becomes a
  scatter. An exploratory question is sufficient; a conclusion is not required in advance.
- **UNIT** is the most common source of error. If "what is one row" is fuzzy, you end up
  double-counting the same entity, or counting summit-level rows as if they were
  interval-level. Not being able to write down n means you don't yet understand the data.
- **MAP** is the design of the figure itself (this is ggplot2's and Vega-Lite's central
  insight: a chart is a mapping from data to visual channels). Writing it down is how you
  catch a key quantity sitting on the wrong channel.
- **SOURCE** lets you answer "where did this number come from" six months later.
  `figstyle.save(provenance=...)` writes it into the file metadata so figure and data stay
  bound together.

For exploratory work, state a sensible question and proceed with a descriptive plot.
Ask only when the missing choice materially changes the meaning, such as the sampling
unit or requested comparison. Never select or filter data to make a desired conclusion
appear. Scale the process: a quick plot needs a brief spec and checks relevant to it;
journal-specific geometry is needed for submission work.

---

## Step 2: choose the chart by encoding effectiveness, not from a chart catalog

The eye reads **position** most accurately and **hue/area** least accurately. This ordering
comes from the psychophysical results of Cleveland & McGill (1984) and Mackinlay (1986),
and it underlies the default rules in Vega-Lite and Observable Plot:

> **Common-scale position > non-aligned position > length > slope/angle > area > volume >
> color value > hue**

Which yields one self-generating rule:

> **Put the quantity you want readers to compare on a position channel.** Secondary
> grouping information goes to color, shape, or faceting.

Consequences (more useful than a chart-type lookup table):

- Comparing magnitudes → dot plot or bars (position/length). **Not** a pie (angle), not
  bubbles (area).
- Comparing two groups → plot the **difference** and its CI. Stronger than drawing the two
  groups side by side, because it puts the comparison itself on a position channel.
- Too many dimensions → **facet (small multiples)**, not a fifth color. `facet_wrap` is
  ggplot2's most-imitated feature precisely because repeated small panels read better than
  one crowded panel.
- More than 8 categories → color has already failed. Facet, or color 2–3 protagonists and
  draw the rest in pale gray.

Locating the chart family from the claim (full decision tree and counter-examples in
`references/chart_choice.md`):

| When the claim is… | Family | First choice |
|---|---|---|
| A is higher/lower than B | magnitude | Dot plot with every point; sorted horizontal bars when there are many groups |
| The **difference** between A and B is non-zero | deviation | Difference dot plot + CI, bold zero line |
| Larger X goes with larger Y | correlation | Scatter + fit + n and effect size; hexbin when dense |
| What the distribution looks like | distribution | Histogram/KDE; box+points or ridgeline across groups |
| It changes with time or dose | trend | Line + error band (x must be an ordered continuum) |
| Who ranks where | ranking | Sorted horizontal bars with values labeled |
| What it is composed of | part-to-whole | Stacked bars; a few labeled slices can serve a simple part-to-whole overview |
| Pairwise / matrix structure | matrix | Heatmap (viridis for sequential; RdBu_r + vcenter=0 when zero is meaningful) |
| How sets overlap | set | Venn up to 3 sets, **UpSet from 4** |
| Position along a coordinate | spatial | Stacked tracks sharing x |

---

## Step 3: choose a tool

Default to **matplotlib + `scripts/figstyle.py`** for explicit physical size, point-sized
type, and vector export. Preserve an existing suitable plotting stack. Others as needed:

| Situation | Use | Why |
|---|---|---|
| Static paper figure (default) | matplotlib + figstyle | Exact size/type control; controllable PDF font subsetting |
| Grouped statistical plots, less code | seaborn (`catplot`/`relplot`/`objects`) | Faceting in one line |
| You think in ggplot2 | plotnine | Same API as R ggplot2; complete facet/scale system |
| Store the figure as a reusable spec | Altair / Vega-Lite | Encoding channels declared explicitly; spec is JSON and versionable |
| Interactive supplement (HTML) | plotly / bokeh | Validate physical size and fonts separately if exporting a static version |
| Tens of millions of points | datashader / holoviews | Aggregate before rendering to avoid overplotting |
| Journal style sheets | SciencePlots | figstyle ships equivalent presets |
| Complex heatmaps (clustering + annotation bars) | R's ComplexHeatmap is the gold standard; in Python, PyComplexHeatmap / marsilea | Annotation bars share coordinates with the main panel; unified legend management |
| Set intersections ≥4 | upsetplot | Venn diagrams are unreadable from four sets up |
| Sequence motif logos | logomaker | Consumes PWM/CWM matrices directly |
| Coordinate/genome tracks | pyGenomeTracks | Track alignment, native bigWig support |
| Circular genome layouts | pyCirclize | |
| Significance annotation | statannotations, or `figstyle.sig_bracket` | Use the latter when statannotations isn't installed |
| Web / dashboard / interactive | a dataviz skill | Out of scope here |

Tool choice affects only *how you draw*. It does **not** affect steps 1–2 or 5–7 — the
spec, the encoding principles, the assertions, the checks, and the export rules apply
identically to every tool.

---

## Step 4: draw

```python
"""
CLAIM/UNIT/MAP/SOURCE — the four lines go here.
"""
import sys; sys.path.insert(0, "<skills>/scifig/scripts")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import use_style, figure_size, categorical, finalize, panel_labels, save
from figcheck import audit, report, preview, cvd_preview

info = use_style("nature", lang="en")      # print it: reports metric-compatible substitutes
print(info)
fig, axes = plt.subplots(1, 2, figsize=figure_size("nature", cols=2, ratio=0.42))
...                                         # then use the native matplotlib API as usual
finalize(fig)                               # resolve layout (do not use subplots_adjust)
panel_labels(fig)                           # a/b/c, aligned in figure coordinates
```

A few things that decide success outright:

- **figsize fixes the final size once**, and nothing is rescaled after export. matplotlib
  type sizes are absolute points: a 7 in figure scaled to 3.5 in inside Word turns 8 pt
  into 4 pt, and the journal's automated check bounces it.
- **Color is never the only encoding.** Use `categorical(n)` (Okabe-Ito, CVD-safe) *and*
  vary line style or marker — the figure has to survive grayscale printing and red–green
  color vision deficiency.
- **Define uncertainty.** Name SD, SEM, or the CI method in the caption and identify the
  independent sampling unit. SEM = SD/√n assumes independent observations; a 95% CI is
  not universally ±1.96 SEM. Preserve pairing and clustering in estimation or resampling.
  Do not add a statistical test or fabricate error bars when only summary values exist.
- **When n is small, draw the points** (`box_strip` / `jitter`). A mean bar with one error
  bar hides the distribution, the outliers, and the true n; the first reviewer comment will
  be "show individual data points". Exception: **deterministic single values** (fixed-seed
  pipeline outputs, single measurements) are not samples — the small-n warning does not
  apply. List them as points; no box, no bar.
- **Connect categories only when the connection means something**, such as the same
  participant measured in two conditions. Identify the pairing; unrelated categories
  should not look like a continuous trajectory.

Complete copy-pasteable recipes per chart type (heatmaps, volcano, ROC, UMAP, ridgeline,
sequence logos, coordinate tracks, multi-panel) are in `references/recipes.md`.

---

## Step 5: verify the plotted values and any claim

Compute data-derived labels from the exact plotted data, after the displayed filters.
Reference thresholds may be specified constants with a source. Check sample counts,
missingness, units, and transformations even for exploratory plots. If a numerical claim
is made, check that its strength matches the computed result:

```python
import numpy as np

if plotted_df[["group", "response"]].isna().any().any():
    raise ValueError("Resolve missing values under the authorized policy before aggregation")
summary = plotted_df.groupby("group")["response"].mean()  # same rows used to draw
difference = summary["treated"] - summary["control"]
if not np.isfinite(difference):
    raise ValueError("Cannot report a mean difference from non-finite group means")
ax.set_title(f"Observed mean difference: {difference:.2f}")
```

Drift between text and figure can occur when a filter changes or an upstream step is
re-run while the figure still reflects older results. Deriving labels from the plotted
values prevents stale annotations; explicit checks catch invalid inputs or unsupported claims.
If a check fails, investigate the inputs and computation. When the computation is sound,
revise or remove the claim; do not weaken the check just to make the figure pass.
An observed difference alone does not establish statistical significance or causality.

---

## Step 6: check, then look

```python
report(audit(fig, min_pt=info["min_pt"]))       # deterministic defects: the computable ones
png = preview(fig, "figs/_check.png")           # then Read this PNG with the Read tool
cvd_preview(png)                                # CVD + grayscale simulations — read those too
```

`audit` catches eight **computable** problems: missing glyphs, text out of bounds,
colliding ticks, type below the journal floor, rainbow colormaps, a continuous color
mapping with no colorbar, a legend covering data points, and a truncated bar baseline.
Any FAIL must be fixed before moving on.

What `audit` cannot catch requires **actually reading the figure with the Read tool**: is
the claim visible at a glance, are panel weights balanced, does an annotation cover key
data, is the whitespace awkward. The checklist is in `references/review.md`.

Running the program is not the same as having seen the figure. Both, or the figure is not
done.

---

## Step 7: export

```python
save(fig, "figs/fig3", formats=("pdf", "png"), dpi=600,
     provenance={"data": "…/marks_summary.parquet", "script": __file__,
                 "claim": "treated 90% vs control 1%"})
```

- **Vector first**: lines, scatter, bars, boxplots → PDF or SVG. Only micrographs,
  photographs, and enormous point clouds justify PNG/TIFF (≥300 dpi; 600 dpi for line art).
- **Never JPEG for data figures**: compression artifacts ring along line edges, and journal
  PDF preflight rejects them.
- **Don't finish with `bbox_inches='tight'`**: it changes the final size, which contradicts
  pinning to column width. Layout problems belong in `finalize()`.
- After writing, `python figcheck.py figs/fig3.pdf --inches 7.2 3.0` verifies size and font
  embedding. A prefix like `ABCDEF+NimbusSans` inside the PDF is the standard notation for
  **a subset that IS embedded** — not for "missing".

The CLI exits 1 for `FAIL`, 0 otherwise; `--strict` also fails on `WARN`, including skipped
checks. Raster checks cover both DPI axes and both physical dimensions. PDF inspection
requires `pypdf` and covers the first page; multi-page files produce a warning. SVG file
inspection is unsupported: audit the Figure before export and inspect a PNG preview.
`--cvd` previews of vector files use `pymupdf`. A clean file check
does not establish scientific validity or replace visual inspection.

---

## Caption template

A caption must stand alone without the main text. Include uncertainty and statistics
lines only when those quantities were actually computed:

```
Figure 3. <supported conclusion or descriptive title for an exploratory figure>.
(a) <what is plotted>. Points = <what one row is>, n = <n per group>.
Error bars = <SD / SEM / 95% CI — say which>.
Statistics = <test and correction, if performed>; describe the sampling unit and pairing.
Data source: <file / pipeline>.
```

Annotating **exact p values** beats stars — stars discard both precision and effect size,
and a growing number of journals require exact values.

---

## When to push back, and how

Preserve a specified chart type and parameters. If a choice materially misrepresents the
data, explain the issue and use an authorized correction, or ask for the smallest needed
decision. Do not deliver a knowingly misleading figure as final or silently change the
analysis to fit a chart. An alternative figure is optional, not a mandatory extra.

Material issues include truncated bar baselines, artificial trajectories across unrelated
categories, dual axes manufacturing a correlation, a continuous mapping without a scale,
or significance annotations without a performed test. Judge the actual encoding: a paired
slope plot and a small labeled pie are not automatically invalid.

Need not be raised (preference only): whether the palette is pretty, gridlines or not, font
taste, legend placement — do what the user said.

The full list of 16 misleading practices and their causes is at the end of
`references/chart_choice.md`.

---

## File index

| File | When to read it |
|---|---|
| `scripts/figstyle.py` | Imported on every figure. Journal geometry, fonts, palettes, layout, export |
| `scripts/figcheck.py` | Run after every figure. Deterministic checks + CVD/grayscale simulation |
| `references/chart_choice.md` | Unsure which chart, or judging whether a practice is misleading |
| `references/recipes.md` | Copy-pasteable code per chart type |
| `references/color.md` | Palettes, colormaps, color vision deficiency, too many categories |
| `references/journals.md` | Target journal column widths, type sizes, formats, fonts, CJK typesetting |
| `references/review.md` | The visual review checklist to use while reading the PNG |

Both scripts self-test: `python figstyle.py --selftest`, `python figcheck.py demo`.

Sibling guardrails, if installed: `sourcing-claims` (every number needs a locator — step 5
is how that lands on a figure) and `executing-as-specified` (a specified plot is drawn as
specified, without unrequested extras).
