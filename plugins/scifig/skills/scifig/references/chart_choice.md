# Choosing a chart: from claim to encoding

Contents
1. [Identify the family first](#1-identify-the-family-first)
2. [The encoding-effectiveness ladder](#2-the-encoding-effectiveness-ladder)
3. [Same data, different claims → different charts](#3-same-data-different-claims--different-charts)
4. [Decision paths by data shape](#4-decision-paths-by-data-shape)
5. [Too many dimensions](#5-too-many-dimensions)
6. [Sixteen ways to make a figure lie](#6-sixteen-ways-to-make-a-figure-lie)

---

## 1. Identify the family first

There are hundreds of chart types but only about a dozen kinds of claim. Find the family,
then pick within it. This taxonomy follows the *Financial Times Visual Vocabulary* — the
most widely adopted scheme in the news-graphics world — organized by **what you are
arguing**, not by **what the data looks like**:

| Family | Shape of the claim | Common charts |
|---|---|---|
| **Magnitude** | A is bigger than B | Bars (horizontal, sorted by value), dot plots |
| **Deviation** | A differs from a reference | Difference bars/dots with a zero line, diverging bars |
| **Correlation** | X and Y move together | Scatter, hexbin, bubble (use sparingly), connected scatter |
| **Distribution** | How values are spread | Histogram, KDE, box, violin, ridgeline, ECDF |
| **Change over time** | Varies with time or dose | Line + error band, area, slope chart |
| **Ranking** | Who is first, who is last | Sorted horizontal bars, dot plots, bump charts |
| **Part-to-whole** | What it is made of | Stacked bars, treemap, waffle; a few labeled pie slices for a simple overview |
| **Matrix** | Pairwise relationships | Heatmap, clustered heatmap, correlation matrix, confusion matrix |
| **Set** | How sets overlap | Venn (≤3 sets), **UpSet (≥4 sets)** |
| **Flow** | From where to where | Sankey, chord, river |
| **Spatial** | Position in some coordinate system | Maps, genome tracks, brain maps |

Picking the wrong family is far worse than picking the wrong chart within it: arguing
part-to-whole with a boxplot from the distribution family leaves readers unable to extract
the conclusion at all.

---

## 2. The encoding-effectiveness ladder

Cleveland & McGill (1984) measured, psychophysically, how accurately people read each
visual encoding; Mackinlay (1986) formalized it into automatic chart-choice rules. The
default encodings in Vega-Lite and Observable Plot rest on this. Ordered accurate →
inaccurate:

```
1. Position on a common scale     (heights on one shared axis)   ← smallest error
2. Position on non-aligned scales (position across facets)
3. Length                         (bar length)
4. Slope / angle                  (line steepness, pie wedges)
5. Area                           (bubble size)
6. Volume / curvature             (3-D)
7. Color value / saturation
8. Hue                            (red vs blue)                  ← largest error;
                                    fine for categories, wrong for quantities
```

**The one rule worth memorizing:** put the quantity your claim compares on a position
channel. Everything else — which group, which batch — goes to color, shape, or facet.

Direct consequences:

- Pie charts encode quantity as angle on non-aligned scales. Prefer sorted bars for
  precise comparisons; a few labeled slices can communicate a simple composition.
- Bubble charts encode quantity as area (rung 5), and people systematically underestimate
  large circles. Avoid unless you genuinely need x, y, and size at once and size is
  secondary.
- 3-D bars distort position into a perspective projection; readers cannot even tell which
  bar is taller. There is no situation that calls for them.
- Encoding quantity as color value (heatmaps) is acceptable, but **a colorbar is
  mandatory**, and readers can only extract "roughly which region is high" — so when exact
  values matter, use position, not a heatmap.

---

## 3. Same data, different claims → different charts

One table: 3 cell lines × 4 timepoints × 6 replicates each, of some measured quantity.

| What you want to say | Chart | Why |
|---|---|---|
| The three lines sit at different overall levels | Dot plot grouped by line (all replicates shown), x = line | Comparison on a common-scale position |
| The quantity rises over time | Line + error band, x = time, one line per cell line | Time is an ordered continuum; slope carries the claim |
| **Line A rises faster than line B** | Just those two lines, plus a **difference curve** below | The claim is the difference, so put the difference on a position channel |
| Replicates are highly dispersed | Box/violin with every point, or ECDF | The claim is the shape of the distribution itself |
| The time–response relationship is non-linear | Scatter (x = numeric time) + fit + residuals | The claim lives in the departure from the fit |
| All 12 combinations must be shown | 3×4 facet grid, shared y | 12 colored lines are unreadable; small multiples are readable |

Six completely different figures from one table, all correct — because the claims differ.
**This is why the first line of the figure spec is CLAIM.**

---

## 4. Decision paths by data shape

```
One continuous variable
├── Show the distribution      → histogram (state the bin count) or KDE; small n → ECDF / dot plot
└── Report one summary number  → don't plot it, put it in the text

One categorical variable's counts / proportions
├── Compare magnitudes         → horizontal bars, sorted by value, values labeled directly
└── Show composition           → stacked bars; a few labeled pie slices for a simple overview

One categorical × one continuous
├── n < 3 per group, or deterministic single values → plot the points, no box, no bar
├── n 3–20 per group                                → box + all points overlaid (figstyle.box_strip)
├── n > 20 per group                                → violin/box + sampled points, or ridgeline
└── more than 10 groups                             → sorted horizontal dot plot, or facet

Two continuous
├── < 5000 points       → scatter + fit line + n and effect size (r or R²)
├── > 5000 points       → hexbin / 2-D density / datashader (scatter overplots to a blob)
└── x is ordered time/dose → line + error band

Two categorical × one continuous (matrix)
└── heatmap; sequential viridis, or RdBu_r with vcenter=0 if zero is meaningful

Many variables
├── Pairwise relationships  → correlation-matrix heatmap or scatter matrix (≤8 variables)
├── Clusters after DR       → UMAP/PCA scatter (⚠️ display only, never quantitative evidence)
└── > 20 variables          → clustered heatmap + row/column annotation bars

Sets
├── ≤ 3 sets  → Venn
└── ≥ 4 sets  → UpSet (Venn is unreadable from four sets up)

Sequence / coordinate data
├── Motif matrices          → sequence logo (logomaker)
└── Signal along coordinate → stacked tracks sharing x, one quantity per track
```

---

## 5. Too many dimensions

Try these in order. **Do not solve it by adding colors.**

1. **Facet (small multiples)** — split one dimension into a row of small panels. This is
   ggplot2 `facet_wrap`'s most important contribution and a technique Tufte returns to
   repeatedly: people compare repeated small panels very accurately (rung 2), whereas eight
   colored lines crammed together is rung 8.
2. **Focus and gray** — color 2–3 protagonists, draw the rest as pale gray background
   lines. The reader instantly knows where to look, and "the rest" still supplies
   distributional context.
3. **Switch to a difference or ratio** — two series become one, a dimension disappears, and
   the claim gets stronger.
4. **Split into several figures** — one core conclusion per figure. Five claims in one
   figure is zero claims.
5. **If you truly need many dimensions:** position (x, y) + facet (1) + color (≤5
   categories) is the ceiling. The shape channel reliably distinguishes 4–5 values at most,
   and is only worth using redundantly with color.

---

## 6. Sixteen ways to make a figure lie

Assess the actual encoding and scientific context. Raise material distortions; distinguish
them from preferences or readability improvements. An exploratory figure may answer a
question without asserting a conclusion.

**Potentially misleading (explain the issue and resolve it before final delivery)**

| # | Practice | Why it lies | Instead |
|---|---|---|---|
| 1 | Bar chart y-axis not starting at 0 | Bar length is no longer proportional to value; a tiny difference is inflated into a huge one | `set_ylim(bottom=0)`; to show small differences use a dot plot or difference plot |
| 2 | Line connecting unrelated categories | Implies a trajectory or relationship not in the data | Dot plot or bars; paired slope plots are appropriate when the same unit connects conditions |
| 3 | Dual y-axes for two unrelated quantities | Where the curves cross and diverge is set by the author's choice of scales, not by the data | Two stacked panels sharing x; or standardize both onto one axis |
| 4 | Rainbow / jet colormap | Non-monotonic lightness manufactures false edges and peaks where the data is smooth | viridis / cividis; RdBu_r when zero is meaningful |
| 5 | Continuous color mapping with no colorbar | Readers cannot convert color back to a number | `fig.colorbar(m, label="quantity (unit)")` |
| 6 | Mean bars only, with small n | Hides the distribution, the outliers, and the true n | Overlay every data point |
| 7 | Diverging midpoint unrelated to the scientific reference | Color implies a departure from the wrong baseline | Center at the meaningful reference, such as zero for differences or one for ratios |
| 8 | Significance annotations without the test and correction | Readers cannot judge whether the p value means anything | Caption states the test, the multiple-comparison correction, and n |

**Readability (raise as appropriate)**

| # | Practice | Problem | Instead |
|---|---|---|---|
| 9 | Pie chart for precise comparisons or many categories | Slice angles are difficult to compare accurately | Sorted bars; a few labeled slices are acceptable for a simple part-to-whole overview |
| 10 | Decorative 3-D for otherwise 2-D data | Perspective distorts quantitative comparisons | 2-D; use 3-D when spatial structure itself is the subject |
| 11 | More than 8 categorical colors | Past the limit of reliable discrimination; one color reads as two things | Facet, or focus-and-gray |
| 12 | Legend sitting on the data | Occlusion, plus back-and-forth eye travel | Move the legend outside, or label curves directly |
| 13 | Five claims in one figure | Readers do not know what to look at | Split it |
| 14 | Axes without units | Readers do not know the dimension | Label axes as "quantity (unit)" |
| 15 | Thousands of raw scatter points | Overplotting destroys all density information | hexbin / 2-D density / alpha + subsample |
| 16 | Rescaling in Word or LaTeX after export | Type size changes with it and may drop below the journal floor | Render at final size; never rescale |

**Not errors, though frequently mistaken for errors:**

- "n < 10 per group always requires box + points" — **true for random samples, false for
  deterministic single values.** One number out of a fixed-seed pipeline is not a sample;
  drawing a box pretends there is a distribution. Plot the values as points.
- Truncating the y-axis — legitimate for quantities with no meaningful zero (temperature,
  pH, ratios, calendar years). It only lies when mark *length* encodes the value (bars,
  areas). Truncating a line chart's y-axis is usually fine.
- Log axes — correct for data spanning orders of magnitude, as long as the axis label says
  it is a log scale.
