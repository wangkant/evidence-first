# Eyes-on review: the half a program cannot see

`figcheck.audit()` catches defects that can be **computed**. The rest you have to
**actually look at** — read the PNG that `preview()` renders, with the Read tool.
Running the checker is not the same as having seen the figure.

```python
png = preview(fig, "figs/_check.png", dpi=160)   # then Read this file
cvd_preview(png)                                  # Read the CVD and grayscale versions too
```

---

## Nine questions to ask while looking

**1. Three-second test: without reading the caption, can you state the figure's conclusion in three seconds?**
If not, the problem is usually the encoding — the quantity being compared isn't on a
position channel, or the claim is buried among elements of equal visual weight. What
you go back and change is the chart type, not the colors.

**2. Does the visual center of gravity land on the claim?**
The eye goes first to whatever is largest, darkest, most saturated. If that's the
gridlines, the legend box, or a secondary series, the weighting is wrong. Make the
protagonist bolder and more saturated; make the supporting cast gray and thin.

**3. Is anything sitting on top of the data?**
Legends, significance annotations, text labels, error-bar caps. A program can compute
how many points a legend covers, but not that the legend covers *the one outlier that
matters*.

**4. Multi-panel: are the panels aligned?**
Top and bottom edges within a row, left and right edges within a column, panel labels
with each other. `finalize` + `panel_labels` usually guarantee this, but a long y-axis
label or a colorbar inside one subplot will knock it out of true.

**5. Multi-panel: is the same variable the same color in every panel?**
Readers should not have to relearn the legend for each subplot. Changing a variable's
color across panels is the single most reader-hostile multi-panel mistake.

**6. Where axes are shared, are the scales genuinely comparable?**
If two side-by-side panels have different y-ranges but look equally tall, readers will
infer equal effect sizes. If you want them compared, use `sharey=True`; if they cannot
be shared, say so explicitly in the caption.

**7. Is the whitespace balanced?**
One side cramped and the other empty usually means a colorbar, legend, or long labels
are taking asymmetric space. Adjust `width_ratios`, or move the legend below the figure.

**8. In the color-vision-deficiency simulation, are the groups still distinguishable?**
Read `_deuteranopia.png`. If they aren't, add a redundant encoding (line style, marker,
direct labeling) — do **not** just pick two colors that "look more different" to you.
Red and green look maximally different to normal trichromats and identical to dichromats.

**9. In grayscale, does the conclusion still hold?**
Read `_grayscale.png`. This doubles as a black-and-white-print simulation and as a test
of whether your lightness differences are sufficient.

---

## Symptom → cause → fix

| What you see in the PNG | Usually means | Fix |
|---|---|---|
| Text clipped mid-character | Layout never resolved | `finalize(fig)`; if it still overflows, shorten labels or widen figsize |
| Tick numbers colliding | Too many ticks, or labels too long | `MaxNLocator(4)`, `tick_params(rotation=30)`, shorter labels |
| Legend covering the curves | `loc` auto-picked a spot inside the data | `bbox_to_anchor=(1.01, 1)` to move it outside, or label lines directly |
| Subplots not vertically aligned | One subplot has a longer y label | Equalize label lengths, or `fig.align_ylabels()` |
| Panel labels in ragged positions | Hand-written `ax.text` | Use `panel_labels(fig)` |
| Scatter is a solid black blob | Overplotting | hexbin / 2-D density / lower alpha + subsample, and say so in the caption |
| Heatmap shows no structure | Extreme values eat the dynamic range | Quantile clipping (`vmin=q01, vmax=q99`) or a log scale; note it in the caption |
| Line colors indistinguishable | More than ~8 categories | Facet, or focus-and-gray |
| Lots of detail, no visible conclusion | One figure carrying several claims | Split the figure |
| CJK text renders as boxes | Font chain not in effect | `use_style(lang='zh')`; mechanism explained in journals.md |
| The figure just looks "dirty" | Heavy gridlines, all four spines, oversized markers | `use_style` defaults already handle this — don't add them back |

---

## After a fix, go around again

Re-render and re-read after every change. Visual problems play whack-a-mole: move the
legend outside and the axes get narrower, so the ticks start colliding again. Loop until:

- `audit()` reports no FAIL;
- you have read the PNG, the CVD version, and the grayscale version, and all nine
  questions pass;
- the caption states error-bar type, n, and the statistical test.

All three, and the figure is done.
