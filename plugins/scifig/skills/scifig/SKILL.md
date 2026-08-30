---
name: scifig
description: >-
  Use whenever a task will produce any data figure — even if the user only says
  "plot this", "let me see the trend", or hands over a CSV/array/DataFrame and asks
  "how should I show this?". Covers choosing the chart, drawing it, asserting the
  claim numerically, running deterministic defect checks, eyeballing the render, and
  exporting at journal column width. Trigger words: plot, chart, figure, graph,
  visualize, visualization, "what chart should I use", "how do I show this",
  matplotlib, seaborn, ggplot, heatmap, boxplot, violin, scatter, line, bar, error
  bars, significance annotation, UMAP, ROC, volcano plot, sequence logo, genome
  track, palette, colorblind, colorbar, facet, panel, subplot, vector, SVG, PDF,
  DPI, column width, CJK boxes, caption. NOT for diagrams, flowcharts, or
  architecture drawings, and not for interactive web/dashboard charts.
---

# scifig — scientific figures, from claim to submission

## What this skill is for

A scientific figure rarely fails because someone can't drive matplotlib. It fails for one
of three reasons:

1. **The figure has no claim** — data is drawn, but the reader doesn't know what to take
   away;
2. **The encoding lies** — bars starting at 9.8, a rainbow colormap inventing boundaries,
   n=4 hidden behind a mean bar;
3. **The figure and the data disagree** — the text says 0.97, the figure says 0.94, and
   nobody notices.

So the order here is: **pin the claim → choose the encoding → draw → let the script verify
the numbers → run the checker → look at it → export.** The plotting code is the middle
step; the value is at both ends.

Not for schematics, flowcharts, or architecture diagrams. Interactive charts for web pages
or dashboards belong to a dataviz skill, not this one.

---

## Step 1: write a four-line figure spec (30 seconds, saves 80% of the rework)

Before drawing, put these four lines in the plotting script's top docstring:

```
CLAIM:  treated samples show an order-of-magnitude higher response than matched controls (90% vs 1%)
UNIT:   one row = one region; treated n=4,812, control n=4,812 (matched on GC and density)
MAP:    x=group (2 levels)  y=response fold-change  point=each region  error=bootstrap 95% CI
SOURCE: results/marks_summary.parquet, column response_fc
```

Why each line earns its place:

- **CLAIM** determines the chart type. From identical data, "A is higher than B" becomes a
  grouped dot plot, "A rises with dose" becomes a line, "A correlates with B" becomes a
  scatter. Without a claim, chart choice is guesswork.
- **UNIT** is the most common source of error. If "what is one row" is fuzzy, you end up
  double-counting the same entity, or counting summit-level rows as if they were
  interval-level. Not being able to write down n means you don't yet understand the data.
- **MAP** is the design of the figure itself (this is ggplot2's and Vega-Lite's central
  insight: a chart is a mapping from data to visual channels). Writing it down is how you
  catch a key quantity sitting on the wrong channel.
- **SOURCE** lets you answer "where did this number come from" six months later.
  `figstyle.save(provenance=...)` writes it into the file metadata so figure and data stay
  bound together.

When the user gives data but no claim: **state your inference and a default plan, then
ask** — "this looks like it's meant to say X, so I'll draw Y; if you actually mean Z, it
should be W instead." Asking "what do you want to say?" empty-handed just hands the work
back.

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
| What it is composed of | part-to-whole | Stacked bars or treemap; **never a pie** |
| Pairwise / matrix structure | matrix | Heatmap (viridis for sequential; RdBu_r + vcenter=0 when zero is meaningful) |
| How sets overlap | set | Venn up to 3 sets, **UpSet from 4** |
| Position along a coordinate | spatial | Stacked tracks sharing x |

---

## Step 3: choose a tool

Default to **matplotlib + `scripts/figstyle.py`**: it is the only stack that pins size to
the inch and type to the point while reliably emitting editable vector output, which is
exactly what submission requires. Others as needed:

| Situation | Use | Why |
|---|---|---|
| Static paper figure (default) | matplotlib + figstyle | Exact size/type control; controllable PDF font subsetting |
| Grouped statistical plots, less code | seaborn (`catplot`/`relplot`/`objects`) | Faceting in one line |
| You think in ggplot2 | plotnine | Same API as R ggplot2; complete facet/scale system |
| Store the figure as a reusable spec | Altair / Vega-Lite | Encoding channels declared explicitly; spec is JSON and versionable |
| Interactive supplement (HTML) | plotly / bokeh | Supplementary only — **never** for print (type size uncontrollable) |
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
- **Error bars must know what they are.** SD, SEM, and 95% CI differ by a √n and a 1.96;
  an error bar whose type isn't in the caption may as well not be drawn.
- **When n is small, draw the points** (`box_strip` / `jitter`). A mean bar with one error
  bar hides the distribution, the outliers, and the true n; the first reviewer comment will
  be "show individual data points". Exception: **deterministic single values** (fixed-seed
  pipeline outputs, single measurements) are not samples — the small-n warning does not
  apply. List them as points; no box, no bar.
- **Never connect points across a categorical axis.** A line implies intermediate states
  between the two points, and a categorical axis has none.

Complete copy-pasteable recipes per chart type (heatmaps, volcano, ROC, UMAP, ridgeline,
sequence logos, coordinate tracks, multi-panel) are in `references/recipes.md`.

---

## Step 5: make the script assert the claim

**Every number on the figure is computed from the data, never typed in.** Then have the
script assert the CLAIM:

```python
hi = df.loc[df.group == "treated", "response_fc"].mean()
lo = df.loc[df.group == "matched", "response_fc"].mean()
assert hi / lo > 5, f"CLAIM says order-of-magnitude; actual {hi:.3f} vs {lo:.3f} = {hi/lo:.1f}×"
ax.set_title(f"{hi/lo:.0f}× higher")        # the title comes from the data too
```

Why this step is not optional: drift between the text and the figure is the most common
and hardest-to-self-catch error in research — a filter changed, an upstream step was
re-run, and the figure is still the old one. The assertion makes **the script crash when
the figure and the claim disagree**, instead of quietly producing a beautiful wrong figure.
If the data changed and the assertion fails, the thing to change is the claim.

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

---

## Caption template

A caption must stand alone without the main text. Figures with error bars or tests
**must** carry all of it:

```
Figure 3. <one-sentence conclusion, not "bar chart of X">.
(a) <what is plotted>. Points = <what one row is>, n = <n per group>.
Error bars = <SD / SEM / 95% CI — say which>.
Statistics = <test>, <multiple-comparison correction>; p values annotated on the figure.
Data source: <file / pipeline>.
```

Annotating **exact p values** beats stars — stars discard both precision and effect size,
and a growing number of journals require exact values.

---

## When to push back, and how

When the user has already specified the chart type and parameters: **do it**. Only speak up
if that choice would make the figure **lie**, and then say it in one sentence, still
produce the figure, and attach an alternative version if warranted.

Must be raised (the figure will mislead readers): truncated bar baselines, lines across
categorical axes, dual y-axes manufacturing a correlation, rainbow colormaps, missing
colorbars, n hidden behind a mean bar, pies comparing angles, significance annotations with
no stated test.

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

