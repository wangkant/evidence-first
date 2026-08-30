# Color

Contents
1. [Three palette types — don't mix them up](#1-three-palette-types--dont-mix-them-up)
2. [Qualitative (categories)](#2-qualitative-categories)
3. [Sequential (magnitude)](#3-sequential-magnitude)
4. [Diverging (a meaningful zero)](#4-diverging-a-meaningful-zero)
5. [Color vision deficiency and grayscale](#5-color-vision-deficiency-and-grayscale)
6. [Too many categories](#6-too-many-categories)
7. [Common color mistakes](#7-common-color-mistakes)

---

## 1. Three palette types — don't mix them up

This is Cynthia Brewer's ColorBrewer rule, since adopted by every major visualization
library:

| Type | Data it belongs on | How to tell |
|---|---|---|
| **Qualitative** | Unordered categories (cell line, treatment arm, model) | Similar lightness, spread hues — implies no magnitude |
| **Sequential** | Ordered, one-directional magnitude (coverage, expression, density) | Lightness varies monotonically — larger is visible at a glance |
| **Diverging** | Quantities with a meaningful zero (log2FC, differences, correlations) | Two hues at the ends, light/neutral in the middle |

Getting this wrong has substantive consequences: a sequential palette on unordered
categories makes readers infer an ordering between them; a sequential palette on log2FC
collapses gains and losses into the same visual direction.

---

## 2. Qualitative (categories)

Default to the **Okabe & Ito (2008)** eight-color palette — designed to be simultaneously
distinguishable under the three main color-vision types, and the de facto standard for
scientific categorical color. `figstyle.categorical(n)` returns it directly:

```
#0072B2 blue     #E69F00 orange   #009E73 green    #CC79A7 reddish purple
#56B4E9 sky blue #D55E00 vermilion #F0E442 yellow  #000000 black
```

Alternatives — **Paul Tol**'s three sets (`figstyle.TOL_BRIGHT/TOL_MUTED/TOL_HIGH_CONTRAST`):

- `TOL_BRIGHT` (7 colors): lines and scatter. High saturation, so thin lines stay visible.
- `TOL_MUTED` (9 colors): filled areas, stacked regions. Lower saturation, so large blocks
  don't shout.
- `TOL_HIGH_CONTRAST` (3 colors, `#004488 #DDAA33 #BB5566`): for 2–3 categories that
  **must** survive black-and-white printing — these three have large lightness separation.

**Redundant encoding**: give categories a different line style or marker in addition to
color. Then the figure survives color-vision deficiency, black-and-white printing, and a
projector with bad color balance.

```python
for (x, y), c, m, ls in zip(series, categorical(3), "os^", ["-", "--", ":"]):
    ax.plot(x, y, color=c, marker=m, linestyle=ls)
```

---

## 3. Sequential (magnitude)

Use a **perceptually uniform** colormap: equal numeric differences look equally different
anywhere along the map.

| Colormap | When |
|---|---|
| `viridis` | Default. Perceptually uniform, CVD-safe, readable in grayscale |
| `cividis` | Optimized for color-vision deficiency; dichromats see nearly what trichromats see |
| `magma` / `inferno` | Dark backgrounds, or when high values should pop |
| `Blues` / `Greys` | Single hue — good when the figure already encodes something else in color |

matplotlib already defaults to viridis; `figstyle.use_style()` also sets `image.cmap` to it.

**Never use `jet` / `rainbow` / `nipy_spectral`.** Their lightness is not monotonic in the
value, which manufactures false edges and false peaks where the data is smooth. This is
not an aesthetic objection — readers see structure that is not in the data
(Borland & Taylor 2007). `figcheck.audit()` scores this as FAIL.

`turbo` is Google's repair of jet (lightness genuinely monotonic now) but is still not
CVD-safe; skip it unless you have a specific reason, such as reproducing an older figure.

---

## 4. Diverging (a meaningful zero)

For log2 fold change, differences, correlations, z-scores — quantities where **zero means
something**:

```python
from matplotlib.colors import TwoSlopeNorm
norm = TwoSlopeNorm(vmin=d.min(), vcenter=0, vmax=d.max())   # the point: vcenter=0
im = ax.imshow(d, cmap="RdBu_r", norm=norm)
fig.colorbar(im, ax=ax, label="log2 fold change")
```

**The midpoint must be that meaningful zero**, or the sign of the color decouples from the
sign of the data — the most common and most serious diverging-colormap error. When the
data is asymmetric (say −1 to +5), either pin zero to the middle color with `TwoSlopeNorm`
or clip the range symmetrically (`vmin=-5, vmax=5`) and say so in the caption.

Colormap choice: `RdBu_r` (red = high, blue = low, the biology convention); for better CVD
safety use `PuOr_r` or `BrBG` (red–green dichromats struggle to separate the two ends of
RdBu).

---

## 5. Color vision deficiency and grayscale

About 8% of men and 0.5% of women have a color vision deficiency, overwhelmingly
red–green. Some of your reviewers are among them. The figure may also be printed in
black and white.

```python
from figcheck import preview, cvd_preview
png = preview(fig, "figs/_check.png")
cvd_preview(png)     # writes _deuteranopia.png and _grayscale.png
```

**Read both simulations with the Read tool** and ask: is the same conclusion still
legible? If not, the information is riding entirely on hue — add a redundant encoding
(line style, marker, direct labeling).

Never rely on red vs green alone to separate two groups: it is the worst possible pair.
Red vs blue is far safer.

---

## 6. Too many categories

Color is not an infinitely extensible dimension. Humans reliably separate about **eight**
categorical colors, and that assumes the marks are large enough — on thin lines it is
fewer. Beyond that you get "is that line purple or reddish purple?"

In priority order:

1. **Facet** — one small panel per category. Eight colored lines are unreadable; eight
   small panels are very readable.
2. **Focus and gray** — color only the 2–3 protagonists, draw everything else in
   `color="0.85"` underneath. The reader immediately knows where to look, and the
   background lines still supply distributional context.
3. **Merge categories** — collapse the long tail into "other".
4. **Change the encoding** — if the categories are themselves ordered (timepoints, doses,
   levels), it is not a qualitative variable: use a sequential colormap and add a colorbar.

`figstyle.categorical(n)` warns when n exceeds the palette's capacity. That warning is
telling you to change encoding, not to ignore it.

---

## 7. Common color mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Sequential colormap on unordered categories | Readers infer an ordering that isn't there | Okabe-Ito |
| Sequential colormap on log2FC | Gains and losses collapse into one direction | Diverging + vcenter=0 |
| Diverging colormap with vcenter ≠ 0 | Color sign decouples from data sign | `TwoSlopeNorm(vcenter=0)` |
| `jet` for signal intensity | Manufactures false edges and peaks | viridis |
| Red vs green to separate two groups | 8% of readers see no difference | Blue vs orange (first two Okabe-Ito) |
| Continuous color mapping with no colorbar | Color cannot be converted back to a number | Add a colorbar labeled with quantity and unit |
| Same variable, different color per panel | Reader relearns the legend each time | One variable, one color, figure-wide |
| Semi-transparent overlays producing a third color | Overlap region misread as a new category | Reduce reliance on alpha; facet or hexbin instead |
| Highlight color spent on an unimportant category | Attention pulled to the wrong place | Saturated for the protagonist, gray for the rest |
