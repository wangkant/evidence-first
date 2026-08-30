# Recipes

Every block is copy-pasteable. Shared preamble:

```python
import sys; sys.path.insert(0, "<skills>/scifig/scripts")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from figstyle import (use_style, figure_size, categorical, finalize,
                      panel_labels, save, box_strip, jitter, sig_bracket,
                      SEQUENTIAL, DIVERGING)
from figcheck import audit, report, preview, cvd_preview
use_style("nature")
```

Contents
1. [Group comparison](#1-group-comparison)  2. [Differences with CIs](#2-differences-with-cis)
3. [Small multiples](#3-small-multiples)  4. [Focus-and-gray multi-series lines](#4-focus-and-gray-multi-series-lines)
5. [Scatter and correlation](#5-scatter-and-correlation)  6. [Distributions](#6-distributions)
7. [Heatmaps](#7-heatmaps)  8. [Clustered heatmap with annotation bars](#8-clustered-heatmap-with-annotation-bars)
9. [ROC / PR](#9-roc--pr)  10. [Volcano plot](#10-volcano-plot)
11. [Dimensionality-reduction scatter (UMAP/PCA)](#11-dimensionality-reduction-scatter-umappca)  12. [Set intersections (UpSet)](#12-set-intersections-upset)
13. [Sequence logo](#13-sequence-logo)  14. [Coordinate tracks](#14-coordinate-tracks)
15. [Multi-panel composition](#15-multi-panel-composition)

---

## 1. Group comparison

With small samples, always draw the points. `box_strip` omits the box when n < 3 (three
points do not have a distribution to draw) and returns each group's n for the caption.

```python
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
ns = box_strip(ax, {"ctrl": ctrl_vals, "KO": ko_vals, "rescue": res_vals})
ax.set_xlabel("condition"); ax.set_ylabel("response (fold-change)")
sig_bracket(ax, 0, 1, ax.get_ylim()[1] * 0.92, "p=0.003")   # exact p, not stars
print(f"caption needs: n = {ns}")
finalize(fig)
```

Above ~10 groups, switch to a **sorted horizontal dot plot** (people compare horizontal
lengths more accurately, and long labels fit):

```python
order = np.argsort(means)
ax.errorbar(means[order], np.arange(len(order)), xerr=ci[order],
            fmt="o", ms=3, lw=0.8, capsize=2)
ax.set_yticks(range(len(order))); ax.set_yticklabels(np.array(labels)[order])
ax.set_xlabel("effect size (95% CI)")
```

---

## 2. Differences with CIs

When the claim is "A and B differ", **plot the difference directly** — it beats plotting
the two groups side by side, because it puts the act of comparison itself on a position
channel and the reader does no mental arithmetic.

```python
fig, ax = plt.subplots(figsize=figure_size("nature", 1, ratio=0.9))
y = np.arange(len(names))
ax.axvline(0, color="0.4", lw=0.8, zorder=1)          # the zero line anchors this figure
ax.errorbar(delta, y, xerr=[delta - lo, hi - delta], fmt="o", ms=3.5,
            lw=0.8, capsize=2, color=categorical(1)[0], zorder=3)
ax.set_yticks(y); ax.set_yticklabels(names)
ax.set_xlabel("Δ AUROC (model − baseline), 95% CI")
ax.set_ylabel("")
ax.invert_yaxis()
```

A CI crossing zero means "no evidence for a difference" — this figure shows that honestly,
whereas side-by-side bars do not.

---

## 3. Small multiples

The default answer when there are many dimensions. Shared axes make panels comparable:

```python
keys = sorted(df["group"].unique())
ncol = 4; nrow = int(np.ceil(len(keys) / ncol))
fig, axes = plt.subplots(nrow, ncol, figsize=figure_size("nature", 2, ratio=0.5),
                         sharex=True, sharey=True)
for ax, k in zip(axes.flat, keys):
    d = df[df.group == k]
    ax.plot(d.x, d.y, lw=1)
    ax.set_title(k, fontsize=plt.rcParams["font.size"])
for ax in axes.flat[len(keys):]:
    ax.set_visible(False)
fig.supxlabel("position"); fig.supylabel("signal")
finalize(fig)
```

⚠️ After `sharey`, do **not** call `set_yticks(labels=[])` on a dependent axis — it wipes
the primary axis's labels too. Hide them with `ax.tick_params(labelleft=False)`.

---

## 4. Focus-and-gray multi-series lines

Eight colored lines are unreadable; two colored lines over a gray field are very readable.

```python
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
for name, y in all_series.items():                      # background
    ax.plot(x, y, color="0.85", lw=0.6, zorder=1)
for (name, y), c, ls in zip(focus.items(), categorical(2), ["-", "--"]):
    ax.plot(x, y, color=c, lw=1.4, ls=ls, zorder=3, label=name)
    ax.annotate(name, (x[-1], y[-1]), xytext=(3, 0), textcoords="offset points",
                color=c, va="center")                   # direct labels beat a legend
ax.set_xlabel("position"); ax.set_ylabel("signal")
```

Labeling at the end of each line beats a legend: the reader never has to look back and
forth between legend and curve.

---

## 5. Scatter and correlation

```python
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
if len(x) <= 5000:
    ax.scatter(x, y, s=4, alpha=0.5, lw=0, color=categorical(1)[0], rasterized=True)
else:
    hb = ax.hexbin(x, y, gridsize=50, cmap=SEQUENTIAL["default"], mincnt=1,
                   linewidths=0)
    fig.colorbar(hb, ax=ax, label="count")              # a color mapping requires a colorbar
from scipy.stats import spearmanr
rho, p = spearmanr(x, y)
lim = [min(x.min(), y.min()), max(x.max(), y.max())]
ax.plot(lim, lim, ls=":", lw=0.8, color="0.4", zorder=1) # identity line (same units only)
ax.set_aspect("equal"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("baseline model score"); ax.set_ylabel("new model score")
ax.set_title(f"ρ = {rho:.2f}, n = {len(x):,}")          # numbers from the data, never typed
assert abs(rho - EXPECTED_RHO) < 0.02, f"CLAIM says {EXPECTED_RHO}, actual {rho:.3f}"
```

`rasterized=True` rasterizes the point layer while text stays vector — the PDF does not
balloon to tens of MB because of 50,000 points.

---

## 6. Distributions

```python
# Histogram: state the bin count, don't take the default
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
ax.hist(v, bins=np.linspace(v.min(), v.max(), 41), color=categorical(1)[0],
        edgecolor="white", lw=0.3)
ax.set_xlabel("score"); ax.set_ylabel("count")

# ECDF: no bin choice needed; fairer than histograms for comparing groups
for (name, v), c in zip(groups.items(), categorical(len(groups))):
    s = np.sort(v)
    ax.step(s, np.arange(1, s.size + 1) / s.size, where="post", color=c, label=name)
ax.set_ylabel("cumulative fraction")

# Ridgeline: stack group distributions vertically — readable where 8 overlapping KDEs are not
for i, (name, v) in enumerate(groups.items()):
    xs = np.linspace(lo, hi, 200)
    d = gaussian_kde(v)(xs); d = d / d.max() * 0.9
    ax.fill_between(xs, i, i + d, color=categorical(len(groups))[i], alpha=0.7, lw=0)
    ax.plot(xs, i + d, color="white", lw=0.5)
ax.set_yticks(range(len(groups))); ax.set_yticklabels(groups)
```

---

## 7. Heatmaps

```python
# Sequential quantity
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
im = ax.imshow(M, cmap=SEQUENTIAL["default"], aspect="auto",
               vmin=np.nanquantile(M, 0.01), vmax=np.nanquantile(M, 0.99))
fig.colorbar(im, ax=ax, label="coverage (RPKM)", fraction=0.046, pad=0.02)

# Diverging quantity: the midpoint must be the meaningful zero
from matplotlib.colors import TwoSlopeNorm
im = ax.imshow(D, cmap=DIVERGING["default"], aspect="auto",
               norm=TwoSlopeNorm(vmin=D.min(), vcenter=0, vmax=D.max()))
fig.colorbar(im, ax=ax, label="log2 fold change")
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right")
```

Quantile clipping (1%/99%) is necessary: a handful of extreme values will eat the whole
dynamic range and flatten the body of the data to a single color. If you clip, say so in
the caption.

---

## 8. Clustered heatmap with annotation bars

R's ComplexHeatmap is the gold standard here; without seaborn or PyComplexHeatmap in
Python, hand-rolling with scipy + GridSpec is not hard and is fully controllable:

```python
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist

Z = linkage(pdist(M, "correlation"), "average")
order = dendrogram(Z, no_plot=True)["leaves"]
Mo = M[order]

fig = plt.figure(figsize=figure_size("nature", 1.5, ratio=0.8))
gs = fig.add_gridspec(1, 3, width_ratios=[0.12, 0.04, 1], wspace=0.02)
axd = fig.add_subplot(gs[0]); axa = fig.add_subplot(gs[1]); axh = fig.add_subplot(gs[2])

dendrogram(Z, ax=axd, orientation="left", no_labels=True,
           link_color_func=lambda _: "0.3")
axd.set_axis_off()
# Annotation bar: which class each row belongs to
cmap_ann = matplotlib.colors.ListedColormap(categorical(len(set(labels))))
axa.imshow(np.array([labels])[:, order].T, aspect="auto", cmap=cmap_ann)
axa.set_axis_off()
im = axh.imshow(Mo, aspect="auto", cmap=SEQUENTIAL["default"])
axh.set_yticks([]); axh.set_xticks(range(len(cols)))
axh.set_xticklabels(cols, rotation=45, ha="right")
fig.colorbar(im, ax=axh, label="z-score", fraction=0.03, pad=0.02)
finalize(fig, engine=None)     # hand-built GridSpec: don't let constrained layout move it again
```

If `PyComplexHeatmap` or `marsilea` is installed, use them — annotation bars share
coordinates with the main panel and legends are managed centrally, which is sturdier than
hand-rolling.

---

## 9. ROC / PR

```python
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score
fig, axes = plt.subplots(1, 2, figsize=figure_size("nature", 2, ratio=0.42))
for (name, s), c in zip(scores.items(), categorical(len(scores))):
    fpr, tpr, _ = roc_curve(ytrue, s); a = auc(fpr, tpr)
    axes[0].plot(fpr, tpr, color=c, label=f"{name} (AUC {a:.3f})")
    pr, rc, _ = precision_recall_curve(ytrue, s)
    axes[1].plot(rc, pr, color=c, label=f"{name} (AP {average_precision_score(ytrue, s):.3f})")
axes[0].plot([0, 1], [0, 1], ls=":", lw=0.8, color="0.5")     # chance baseline
axes[1].axhline(ytrue.mean(), ls=":", lw=0.8, color="0.5")    # PR chance = positive rate
axes[0].set(xlabel="false positive rate", ylabel="true positive rate")
axes[1].set(xlabel="recall", ylabel="precision")
for ax in axes: ax.legend(loc="lower right" if ax is axes[0] else "upper right")
```

Draw both baselines: the diagonal for ROC, the positive-class rate for PR (under class
imbalance the "passing mark" for AP is not 0.5).

---

## 10. Volcano plot

```python
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
sig = (padj < 0.05) & (np.abs(lfc) > 1)
ax.scatter(lfc[~sig], -np.log10(padj[~sig]), s=3, lw=0, color="0.8", rasterized=True)
ax.scatter(lfc[sig], -np.log10(padj[sig]), s=4, lw=0,
           color=categorical(2)[0], rasterized=True)
ax.axvline(0, color="0.4", lw=0.6)
for thr in (-1, 1): ax.axvline(thr, ls=":", lw=0.6, color="0.5")
ax.axhline(-np.log10(0.05), ls=":", lw=0.6, color="0.5")
for g in top_genes:                                    # label a handful, don't carpet it
    ax.annotate(g, (lfc[g], -np.log10(padj[g])), fontsize=5,
                xytext=(2, 2), textcoords="offset points")
ax.set_xlabel("log2 fold change"); ax.set_ylabel("−log10 adjusted p")
ax.set_title(f"{sig.sum()} significant of {len(lfc)}")
```

---

## 11. Dimensionality-reduction scatter (UMAP/PCA)

```python
fig, ax = plt.subplots(figsize=figure_size("nature", 1))
for (name, idx), c in zip(groups.items(), categorical(len(groups))):
    ax.scatter(emb[idx, 0], emb[idx, 1], s=2, lw=0, alpha=0.6, color=c,
               label=name, rasterized=True)
ax.set_xlabel("UMAP 1"); ax.set_ylabel("UMAP 2")
ax.set_xticks([]); ax.set_yticks([])          # absolute UMAP axis values are meaningless
ax.set_aspect("equal")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), markerscale=3)
```

⚠️ UMAP/t-SNE plots are **display only, never quantitative evidence**: between-cluster
distances, cluster sizes, and cluster shapes are all unfaithful, and everything depends
strongly on hyperparameters. To argue "these two groups are separable" you need a
full-dimensional quantity (classification AUROC, held-out accuracy); the UMAP merely
pictures that conclusion. State the parameters in the caption (n_neighbors, min_dist,
random seed, input dimensionality).

---

## 12. Set intersections (UpSet)

Do not draw a Venn diagram for four or more sets. Use `upsetplot` if installed; a pure
matplotlib version otherwise:

```python
from itertools import combinations
names = list(sets)
combos = []
for r in range(len(names), 0, -1):
    for c in combinations(range(len(names)), r):
        inter = set.intersection(*[sets[names[i]] for i in c])
        excl = inter - set.union(*[sets[names[i]] for i in range(len(names)) if i not in c]) \
               if r < len(names) else inter
        if excl: combos.append((c, len(excl)))
combos.sort(key=lambda t: -t[1]); combos = combos[:15]      # top 15 only
# NOTE: this drops every smaller intersection — say so in the caption.

fig = plt.figure(figsize=figure_size("nature", 1.5, ratio=0.7))
gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.05)
axb = fig.add_subplot(gs[0]); axm = fig.add_subplot(gs[1], sharex=axb)
axb.bar(range(len(combos)), [n for _, n in combos], color="0.25", width=0.6)
axb.set_ylabel("intersection size"); axb.tick_params(labelbottom=False)
for j, (c, _) in enumerate(combos):
    axm.plot([j] * len(names), range(len(names)), "o", ms=4, color="0.85")
    axm.plot([j] * len(c), list(c), "-o", ms=4, color="0.15", lw=1)
axm.set_yticks(range(len(names))); axm.set_yticklabels(names)
axm.set_xticks([]); axm.invert_yaxis()
for s in ("top", "right", "bottom"): axm.spines[s].set_visible(False)
axm.set_xlabel("set combination")
```

---

## 13. Sequence logo

`logomaker` consumes PWM / CWM / contribution matrices directly:

```python
import logomaker, pandas as pd
# mat: (L, 4) DataFrame with columns ACGT. Contribution matrices plot as-is
# (positive and negative values are both meaningful — that is correct).
df = pd.DataFrame(cwm, columns=list("ACGT"))
fig, ax = plt.subplots(figsize=figure_size("nature", 1, ratio=0.3))
logomaker.Logo(df, ax=ax, color_scheme="classic", shade_below=0.5, fade_below=0.5)
ax.set_xlabel("position (bp)"); ax.set_ylabel("contribution")
ax.spines[["top", "right"]].set_visible(False)
```

- Probability matrices must be converted to information content first:
  `logomaker.transform_matrix(df, from_type='probability', to_type='information')`.
  Otherwise every position has height 1 and conservation is invisible.
- Contribution matrices (CWM / hypothetical) must **not** be converted to information
  content — negative contributions are meaningful information, and the transform discards
  them.

---

## 14. Coordinate tracks

Several signals along a shared coordinate, stacked vertically with a shared x. Use
`pyGenomeTracks` if installed (it reads bigWig/bed natively); for a stretch of numpy
signal:

```python
tracks = [("observed", obs, "0.35"), ("predicted", pred, categorical(2)[0]),
          ("attribution", contrib, categorical(2)[1])]
fig, axes = plt.subplots(len(tracks), 1, sharex=True,
                         figsize=figure_size("nature", 2, h=0.6 * len(tracks)),
                         gridspec_kw=dict(hspace=0.12))
for ax, (name, y, c) in zip(axes, tracks):
    ax.fill_between(pos, 0, y, color=c, lw=0)
    ax.set_ylabel(name, rotation=0, ha="right", va="center")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False, labelleft=False)
    ax.margins(x=0)
for m in motif_hits:                                     # feature hits on the bottom track
    axes[-1].axvspan(m.start, m.end, color="0.85", zorder=0)
    axes[-1].annotate(m.name, ((m.start + m.end) / 2, 0), fontsize=5,
                      ha="center", va="top", xytext=(0, -2),
                      textcoords="offset points", rotation=90)
axes[-1].set_xlabel(f"{chrom}:{pos[0]:,}-{pos[-1]:,}")
```

Key points: every track uses `sharex` and `margins(x=0)`, otherwise tracks drift by a few
units relative to each other — and vertical alignment is the entire value of this figure.
Y ticks can be dropped, but **each track's units must be stated** in the track name or the
caption (raw count? fold-change? attribution?).

---

## 15. Multi-panel composition

`subplot_mosaic` describes the layout with a string, which reads far better than nested
GridSpecs:

```python
fig, axd = plt.subplot_mosaic(
    """
    AAB
    CDB
    """,
    figsize=figure_size("nature", 2, ratio=0.62),
    width_ratios=[1, 1, 1.2], height_ratios=[1, 1],
)
# axd["A"], axd["B"] ... draw into each as usual
finalize(fig)
panel_labels(fig, [axd[k] for k in "ABCD"])     # pass the order; don't rely on dict order
save(fig, "figs/fig1", formats=("pdf", "png"), dpi=600,
     provenance={"data": "...", "script": __file__})
```

Three rules for multi-panel figures:

1. **Same variable, same color across panels** — readers should not relearn the legend per
   panel.
2. **Share axes wherever they can be shared**; where they cannot, say in the caption that
   the scales differ.
3. **Use `panel_labels`, never hand-written `ax.text`** — each panel has a different data
   range, so identical relative coordinates land at different physical positions.
