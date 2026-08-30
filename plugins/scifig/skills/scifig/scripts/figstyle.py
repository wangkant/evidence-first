"""
scifig :: figstyle.py — journal geometry, font resolution, palettes, layout, export
                        (with provenance metadata)

Design stance
-------------
Turn the handful of things you would otherwise rewrite on every figure into
functions that are correct once, and leave everything else to the native
matplotlib API — this module does **not** wrap plotting. You still call
``ax.plot`` / ``ax.imshow`` as usual.

Why it does not depend on seaborn / SciencePlots: neither is guaranteed to be
installed, and a figure module that hard-depends on them fails on a bare
scientific-Python environment. The two statistical primitives that come up on
almost every grouped figure (jittered points, significance brackets) are
implemented here in plain matplotlib; having seaborn installed does not conflict.

The four jobs this module owns
------------------------------
1. ``use_style()`` — journal rcParams plus **real font-availability resolution**
   (if Helvetica is absent, use the metric-compatible Nimbus Sans rather than
   silently falling back to DejaVu; for CJK, use a family-fallback chain so Latin
   and CJK glyphs each come from a font that has them).
2. ``figure_size()`` — final size from column width, eliminating "exported then
   rescaled, so the type size is wrong".
3. ``categorical()`` / ``SEQUENTIAL`` / ``DIVERGING`` — CVD-safe discrete colors
   and perceptually uniform colormaps.
4. ``finalize()`` / ``panel_labels()`` / ``save()`` — resolve layout, stamp a/b/c,
   export to several formats and write **the data provenance into the file
   metadata** (costs no space on the page, but figure and data stay tied together).

CLI self-test: python figstyle.py --selftest
"""
from __future__ import annotations

import datetime as _dt
import os
import warnings
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

__all__ = [
    "JOURNALS", "OKABE_ITO", "TOL_BRIGHT", "TOL_MUTED", "TOL_HIGH_CONTRAST",
    "SEQUENTIAL", "DIVERGING", "use_style", "figure_size", "categorical",
    "resolve_font", "finalize", "panel_labels", "save", "jitter", "box_strip",
    "sig_bracket",
]

# --------------------------------------------------------------------------
# Journal geometry
# --------------------------------------------------------------------------
# Inches. col1 / col15 / col2 = usable width at 1 / 1.5 / 2 columns;
# max_h = maximum live-area height.
# ⚠️ These are **working defaults** (collected from the common values in author
#    guides). Before submitting, check them against the current figure guideline
#    of your target journal — journals revise, and this table is not authoritative.
JOURNALS: dict[str, dict] = {
    "default":   dict(col1=3.50, col15=5.00, col2=7.00, max_h=9.00, base=8,
                      font="sans", min_pt=6),
    "nature":    dict(col1=3.50, col15=4.76, col2=7.20, max_h=9.72, base=7,
                      font="helvetica", min_pt=5),
    "science":   dict(col1=2.24, col15=3.74, col2=4.76, max_h=9.00, base=7,
                      font="helvetica", min_pt=6),
    "cell":      dict(col1=3.35, col15=4.49, col2=6.85, max_h=9.00, base=7,
                      font="arial", min_pt=6),
    "pnas":      dict(col1=3.42, col15=4.49, col2=7.00, max_h=9.00, base=8,
                      font="helvetica", min_pt=6),
    "plos":      dict(col1=2.63, col15=5.20, col2=7.50, max_h=8.75, base=8,
                      font="arial", min_pt=8),
    "elife":     dict(col1=3.35, col15=4.72, col2=6.85, max_h=9.00, base=8,
                      font="arial", min_pt=6),
    "nar":       dict(col1=3.39, col15=4.72, col2=7.01, max_h=9.00, base=8,
                      font="arial", min_pt=6),
    "bmc":       dict(col1=3.35, col15=4.72, col2=6.69, max_h=9.00, base=8,
                      font="arial", min_pt=6),
    "elsevier":  dict(col1=3.54, col15=5.51, col2=7.48, max_h=9.00, base=8,
                      font="arial", min_pt=7),
    "ieee":      dict(col1=3.50, col15=5.00, col2=7.16, max_h=8.75, base=8,
                      font="times", min_pt=6),
    "acm":       dict(col1=3.33, col15=5.00, col2=7.00, max_h=9.00, base=8,
                      font="times", min_pt=6),
    "neurips":   dict(col1=5.50, col15=5.50, col2=5.50, max_h=8.00, base=8,
                      font="times", min_pt=7),
    "thesis":    dict(col1=4.50, col15=5.50, col2=6.30, max_h=8.50, base=9,
                      font="times", min_pt=8),
    "slide":     dict(col1=5.00, col15=7.50, col2=10.0, max_h=6.50, base=14,
                      font="sans", min_pt=12),
}

# --------------------------------------------------------------------------
# Fonts: metric-compatible substitution chains
# --------------------------------------------------------------------------
# Journals want Helvetica/Arial/Times, and Linux machines usually have none of
# them. Nimbus Sans (URW) for Helvetica, Liberation Sans for Arial, and
# Nimbus Roman / Liberation Serif for Times New Roman are **metric-compatible**
# clones — identical advance widths and heights, so layout does not shift. That
# is much better than the default silent fallback to DejaVu Sans, which is wider
# and looks visibly different.
_FONT_CHAINS: dict[str, list[str]] = {
    "helvetica": ["Helvetica", "Helvetica Neue", "Arial", "Nimbus Sans",
                  "TeX Gyre Heros", "Liberation Sans", "Arimo", "DejaVu Sans"],
    "arial":     ["Arial", "Liberation Sans", "Arimo", "Helvetica",
                  "Nimbus Sans", "TeX Gyre Heros", "DejaVu Sans"],
    "times":     ["Times New Roman", "Nimbus Roman", "Liberation Serif",
                  "Tinos", "TeX Gyre Termes", "STIXGeneral", "DejaVu Serif"],
    "sans":      ["Helvetica", "Arial", "Nimbus Sans", "Liberation Sans",
                  "Lato", "DejaVu Sans"],
    "serif":     ["Times New Roman", "Nimbus Roman", "Liberation Serif",
                  "STIXGeneral", "DejaVu Serif"],
}
# CJK: note that Droid Sans Fallback is routinely overlooked, yet it ships with
# most Linux distributions and covers all common Han characters — putting it in
# the chain means many "CJK renders as boxes" machines need no font installed.
_CJK_SANS = ["Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC",
             "Source Han Sans CN", "WenQuanYi Zen Hei", "WenQuanYi Micro Hei",
             "Droid Sans Fallback", "Heiti SC", "PingFang SC", "SimHei",
             "Microsoft YaHei", "Arial Unicode MS"]
_CJK_SERIF = ["Noto Serif CJK SC", "Source Han Serif SC", "Songti SC",
              "SimSun", "STSong"] + _CJK_SANS


def _available_fonts() -> set[str]:
    """
    Count only ttflist (TrueType/OpenType). Do **not** merge in afmlist:
    matplotlib ships AFM metrics for the PostScript core fonts (including
    "Helvetica"), but those carry metrics with no glyphs and fall back silently
    at raster/PDF render time — counting them reports "Helvetica available" when
    it is not.
    """
    import matplotlib.font_manager as fm
    return {f.name for f in fm.fontManager.ttflist}


def resolve_font(kind: str = "sans", lang: str = "en") -> tuple[list[str], dict]:
    """
    Resolve "the font the journal wants" into a family list that **actually
    exists on this machine**.

    Returns (family_list, info). family_list goes straight into
    rcParams['font.sans-serif'] or ['font.serif'] — matplotlib >=3.6 falls back
    **per glyph** along the list, so Latin glyphs come from the first Western
    font and CJK glyphs from a later CJK font, and both can coexist in one figure.

    info carries requested / picked / substituted so a log can state honestly
    that the submission font was missed and a metric-compatible substitute was used.
    """
    avail = _available_fonts()
    chain = _FONT_CHAINS.get(kind, _FONT_CHAINS["sans"])
    picked = next((f for f in chain if f in avail), None)
    if picked is None:                       # DejaVu should always exist; belt and braces
        picked = mpl.rcParams["font.sans-serif"][0]
    families = [picked]

    cjk = None
    if lang == "zh":
        cjk_chain = _CJK_SERIF if kind in ("times", "serif") else _CJK_SANS
        cjk = next((f for f in cjk_chain if f in avail), None)
        if cjk:
            families.append(cjk)
        else:
            warnings.warn(
                "No CJK font found; CJK text will render as boxes. Installing one "
                "is enough:  conda install -c conda-forge font-ttf-source-han-sans  "
                "or  apt install fonts-noto-cjk / fonts-droid-fallback",
                RuntimeWarning, stacklevel=2)
    if "DejaVu Sans" in avail and "DejaVu Sans" not in families:
        families.append("DejaVu Sans")       # last resort for math/Greek/⩽-type symbols

    info = dict(requested=chain[0], picked=picked, cjk=cjk,
                substituted=picked != chain[0])
    return families, info


# --------------------------------------------------------------------------
# Palettes
# --------------------------------------------------------------------------
# The Okabe & Ito (2008) eight-color qualitative palette: optimized for the three
# main color-vision types simultaneously, and the de facto scientific standard
# for qualitative color. Black is placed last; the first seven are pairwise
# distinguishable.
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7",
             "#56B4E9", "#D55E00", "#F0E442", "#000000"]
# Paul Tol's palettes: bright suits lines and points, muted suits filled areas
# (lower saturation, so large blocks do not shout).
TOL_BRIGHT = ["#4477AA", "#EE6677", "#228833", "#CCBB44",
              "#66CCEE", "#AA3377", "#BBBBBB"]
TOL_MUTED = ["#332288", "#88CCEE", "#44AA99", "#117733", "#999933",
             "#DDCC77", "#CC6677", "#882255", "#AA4499"]
TOL_HIGH_CONTRAST = ["#004488", "#DDAA33", "#BB5566"]   # separable in grayscale print

_PALETTES = {"okabe_ito": OKABE_ITO, "tol_bright": TOL_BRIGHT,
             "tol_muted": TOL_MUTED, "high_contrast": TOL_HIGH_CONTRAST}

# Continuous colormaps: perceptually uniform and CVD-safe. Never jet/rainbow
# (see references/color.md).
SEQUENTIAL = dict(default="viridis", cvd_safe="cividis", dark_bg="magma",
                  single_hue="Blues", density="mako_r")
# Diverging colormaps: **must** be centred on the meaningful zero (vcenter), or
# the color is lying.
DIVERGING = dict(default="RdBu_r", cvd_safe="PuOr_r", earth="BrBG")


def categorical(n: int, palette: str = "okabe_ito") -> list[str]:
    """
    Take n CVD-safe discrete colors.

    Exceeding the palette's capacity warns rather than silently cycling — one
    color meaning two things is far worse than "the figure isn't pretty".
    More than 8 categories means the encoding should change (facet, or highlight
    2-3 protagonists and gray the rest); see the "too many categories" section of
    references/color.md.
    """
    cols = _PALETTES.get(palette, OKABE_ITO)
    if n > len(cols):
        warnings.warn(
            f"asked for {n} categorical colors, but {palette} only has {len(cols)} "
            "reliably distinguishable ones. Color is not an unlimited dimension: "
            "use small multiples, or color only 2-3 protagonists and draw the rest "
            "as pale gray. Cycling for now, so the figure will have one color "
            "meaning two things.",
            RuntimeWarning, stacklevel=2)
        cols = (cols * (n // len(cols) + 1))
    return list(cols[:n])


# --------------------------------------------------------------------------
# Style
# --------------------------------------------------------------------------
def use_style(journal: str = "default", lang: str = "en",
              base_pt: float | None = None, palette: str = "okabe_ito",
              grid: bool = False) -> dict:
    """
    Apply journal rcParams. Returns what was resolved (fonts, column widths, …) —
    **print it**. "Wanted Helvetica, actually used Nimbus Sans" has to leave a
    trace, or you discover it right before submission.

    Deliberately does **not** enable constrained_layout globally: turning it on
    globally makes ``subplots_adjust`` / ``tight_layout`` silently ineffective,
    which is a hard bug to track down. Layout is handled uniformly by
    ``finalize(fig)``.
    """
    spec = JOURNALS.get(journal, JOURNALS["default"])
    base = float(base_pt if base_pt is not None else spec["base"])
    families, finfo = resolve_font(spec["font"], lang)
    serif_like = spec["font"] in ("times", "serif")

    rc = {
        # ⚠️ Verified on mpl 3.10/3.11: per-glyph fallback only takes effect when
        # font.family is given a list of concrete font names. Writing
        # family='sans-serif' + font.sans-serif=[...] does NOT fall back, and CJK
        # goes straight to boxes — which is where most "CJK boxes" tutorials trip.
        "font.family": families,
        ("font.serif" if serif_like else "font.sans-serif"): families,
        "font.size": base,
        "axes.titlesize": base,
        "axes.labelsize": base,
        "xtick.labelsize": base - 1,
        "ytick.labelsize": base - 1,
        "legend.fontsize": base - 1,
        "figure.titlesize": base + 1,
        # Spines/ticks: thin, outward, top and right removed — higher data-ink
        # ratio, and they stop competing with the data for attention.
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelpad": 2.0,
        "axes.titlepad": 3.0,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
        "lines.linewidth": 1.2,
        "lines.markersize": 3.5,
        "patch.linewidth": 0.5,
        "grid.linewidth": 0.4,
        "grid.alpha": 0.35,
        "axes.grid": bool(grid),
        "legend.frameon": False,
        "legend.handlelength": 1.4,
        "legend.columnspacing": 1.0,
        "legend.labelspacing": 0.3,
        "axes.prop_cycle": mpl.cycler(color=_PALETTES.get(palette, OKABE_ITO)),
        "image.cmap": SEQUENTIAL["default"],
        # Vector export: converting text to outlines stops reviewers searching the
        # text and stops the typesetter nudging it. Keep 42 (TrueType) so PDF/PS
        # embed an editable font subset.
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.transparent": False,
        "savefig.facecolor": "white",
        "figure.dpi": 150,
        "figure.facecolor": "white",
    }
    # matplotlib <3.6 has no per-glyph fallback, and the primary CJK font usually
    # lacks U+2212 — only then does this need turning off.
    rc["axes.unicode_minus"] = tuple(int(x) for x in mpl.__version__.split(".")[:2]) >= (3, 6)
    mpl.rcParams.update(rc)

    info = dict(journal=journal, lang=lang, base_pt=base, min_pt=spec["min_pt"],
                widths={"col1": spec["col1"], "col15": spec["col15"],
                        "col2": spec["col2"]}, max_height=spec["max_h"],
                fonts=families, **finfo)
    return info


def figure_size(journal: str = "default", cols: float = 1,
                h: float | None = None, ratio: float = 0.72) -> tuple[float, float]:
    """
    Give the **final** size in inches from a column width. cols ∈ {1, 1.5, 2}, or
    pass a width directly (anything > 2 is read as inches).

    Why it matters: matplotlib type sizes are absolute points. Render at 7 in,
    scale to 3.5 in inside Word, and 8 pt becomes 4 pt — the journal's automated
    check bounces it. Fix the final size once and **never rescale after export**.
    """
    spec = JOURNALS.get(journal, JOURNALS["default"])
    w = {1: spec["col1"], 1.5: spec["col15"], 2: spec["col2"]}.get(
        cols, float(cols) if cols > 2 else spec["col1"])
    height = float(h) if h is not None else w * ratio
    if height > spec["max_h"]:
        warnings.warn(f"height {height:.2f} in exceeds the {journal} live area of "
                      f"{spec['max_h']} in; you will be asked to shrink or split it.",
                      RuntimeWarning, stacklevel=2)
    return (float(w), height)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def finalize(fig, engine: str = "constrained", pad: float = 0.04) -> None:
    """
    Resolve layout, once. Call it after all drawing and before ``save`` / checks.

    Uses a layout engine rather than a global rcParam: it takes over only at this
    moment, so if you deliberately wrote ``subplots_adjust`` earlier, pass
    engine=None to skip.
    """
    if engine:
        try:
            fig.set_layout_engine(engine, w_pad=pad, h_pad=pad, wspace=0.02,
                                  hspace=0.02)
            fig.canvas.draw()
            return
        except (AttributeError, TypeError):
            pass
        except Exception as e:
            # A hand-built GridSpec (especially with wspace/hspace or zero-width
            # panels) can make constrained layout blow up. A layout failure should
            # not kill the whole plotting script — fall back to tight_layout, and
            # failing that keep the author's own arrangement.
            warnings.warn(f"constrained layout failed ({type(e).__name__}: {e}); "
                          "falling back to tight_layout. For a hand-built GridSpec, "
                          "pass finalize(fig, engine=None) directly.", RuntimeWarning,
                          stacklevel=2)
        try:
            fig.set_layout_engine("none")
            fig.tight_layout(pad=0.4)
        except Exception:
            pass
    fig.canvas.draw()


def panel_labels(fig, axes: Sequence | None = None, style: str = "nature",
                 dx: float = -0.055, dy: float = 0.015, weight: str = "bold",
                 size: float | None = None) -> list:
    """
    Stamp a/b/c labels on a multi-panel figure. Positions are computed uniformly
    in **figure coordinates**, so labels in a column are naturally left-aligned
    and labels in a row are naturally top-aligned. Hand-written ``ax.text`` is the
    most common source of ragged multi-panel labels.

    style: 'nature' → a b c; 'ieee'/'paren' → (a) (b) (c); 'upper' → A B C.
    """
    axs = list(axes) if axes is not None else [a for a in fig.axes
                                               if a.get_subplotspec() is not None
                                               and getattr(a, "_scifig_cbar", False) is False]
    fmt = {"nature": "{}", "upper": "{}", "ieee": "({})", "paren": "({})"}.get(style, "{}")
    letters = "ABCDEFGHIJKLMNOP" if style == "upper" else "abcdefghijklmnop"
    size = size or mpl.rcParams["font.size"] + 1
    fig.canvas.draw()
    out = []
    for i, ax in enumerate(axs):
        bb = ax.get_position()
        # Under tight layouts y1+dy is frequently already > 1, so the label is
        # drawn off-canvas and looks like it "didn't get stamped". Clamp back
        # inside and switch to va='top', hanging the letter just inside the panel's
        # top-left corner — which is exactly the Nature style anyway.
        x = max(bb.x0 + dx, 0.002)
        y = bb.y1 + dy
        va = "bottom"
        if y > 0.998:
            y, va = 0.998, "top"
        out.append(fig.text(x, y, fmt.format(letters[i]), fontsize=size,
                            fontweight=weight, va=va, ha="left"))
    return out


# --------------------------------------------------------------------------
# Statistical primitives (no seaborn dependency; these two get rewritten on
# nearly every figure otherwise)
# --------------------------------------------------------------------------
def jitter(ax, x: float, values, width: float = 0.16, seed: int = 0, **kw):
    """
    Draw a jittered column of points at x. **Any grouped figure with n < 20 should
    overlay this** — a bar height plus an error bar hides the shape of the
    distribution, the outliers, and the true n, and the first reviewer comment
    will be "show individual points".

    The jitter uses a fixed seed so the figure is reproducible (the same data
    plots to the same point positions twice).
    """
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    rng = np.random.default_rng(seed)
    kw.setdefault("s", 8)
    kw.setdefault("linewidths", 0.4)
    kw.setdefault("edgecolors", "white")
    kw.setdefault("zorder", 3)
    return ax.scatter(x + rng.uniform(-width, width, v.size), v, **kw)


def box_strip(ax, groups: dict[str, Iterable] | Sequence[Iterable],
              labels: Sequence[str] | None = None, colors=None,
              box: bool = True, seed: int = 0, width: float = 0.55):
    """
    Box plus every data point — the group-comparison figure most often demanded in
    biological and medical papers.

    When n is small (< 3) the box is dropped automatically and only the points are
    listed: drawing a box over three points pretends there is a distribution.
    Returns each group's n so you can put it in the caption (a caption without n
    has not reported n).
    """
    if isinstance(groups, dict):
        labels = list(groups.keys())
        data = [np.asarray(list(v), dtype=float) for v in groups.values()]
    else:
        data = [np.asarray(list(v), dtype=float) for v in groups]
        labels = list(labels or [str(i + 1) for i in range(len(data))])
    data = [d[np.isfinite(d)] for d in data]
    ns = [d.size for d in data]
    colors = list(colors) if colors is not None else categorical(len(data))
    pos = np.arange(len(data), dtype=float)

    if box and min(ns) >= 3:
        bp = ax.boxplot(data, positions=pos, widths=width, showfliers=False,
                        patch_artist=True, medianprops=dict(color="black", lw=1.0),
                        whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6),
                        boxprops=dict(lw=0.6))
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.28)
            patch.set_edgecolor(c)
    for i, (d, c) in enumerate(zip(data, colors)):
        jitter(ax, pos[i], d, width=width * 0.3, seed=seed + i, color=c)
    ax.set_xticks(pos)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.6, len(data) - 0.4)
    return ns


def sig_bracket(ax, x1: float, x2: float, y: float, text: str,
                h: float | None = None, lw: float = 0.6, color: str = "black",
                pad: float = 0.0, fontsize: float | None = None):
    """
    Draw a significance bracket between groups x1 and x2. Write an **exact p
    value** in `text` (e.g. "p=0.003") rather than stars — stars discard both
    effect size and precision, and a growing number of journals require the exact
    value.
    """
    if h is None:
        lo, hi = ax.get_ylim()
        h = (hi - lo) * 0.02
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=lw, c=color,
            clip_on=False, zorder=5)
    ax.text((x1 + x2) / 2, y + h + pad, text, ha="center", va="bottom",
            fontsize=fontsize or mpl.rcParams["font.size"] - 1, color=color,
            clip_on=False, zorder=5)


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------
def save(fig, basename: str, formats: Sequence[str] = ("pdf", "png"),
         dpi: int = 600, size: tuple[float, float] | None = None,
         provenance: str | dict | None = None, tight: bool = False) -> list[str]:
    """
    Export to several formats and write **the data provenance into the file
    metadata**.

    Use provenance to record which column of which file the numbers came from. It
    takes no space on the page, but six months later, when a reviewer asks where
    the 0.62 in Fig. 3b came from, ``pdfinfo fig3.pdf`` answers.

    tight=False is deliberate: ``bbox_inches='tight'`` **changes the final size**,
    which contradicts pinning the size to a column width. Layout problems belong
    in finalize(), not in cropping them away.
    """
    if size:
        fig.set_size_inches(*size)
    os.makedirs(os.path.dirname(os.path.abspath(basename)) or ".", exist_ok=True)

    if isinstance(provenance, dict):
        prov = "; ".join(f"{k}={v}" for k, v in provenance.items())
    else:
        prov = provenance or ""
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    written = []
    for ext in formats:
        path = f"{basename}.{ext}"
        meta = None
        if ext == "pdf":
            meta = {"Title": os.path.basename(basename), "Subject": prov,
                    "Creator": f"scifig {stamp}"}
        elif ext == "png":
            meta = {"Title": os.path.basename(basename), "Description": prov,
                    "Software": f"scifig {stamp}"}
        elif ext == "svg":
            meta = {"Title": os.path.basename(basename), "Description": prov,
                    "Creator": f"scifig {stamp}"}
        kw = dict(dpi=dpi)
        if meta:
            kw["metadata"] = meta
        if tight:
            kw["bbox_inches"] = "tight"
        if ext in ("jpg", "jpeg"):
            warnings.warn("never use JPEG for a data figure: compression artifacts "
                          "leave ringing along line edges, and many journals' PDF "
                          "preflight rejects it outright. Use PDF/SVG (vector) or "
                          "PNG/TIFF (raster).", RuntimeWarning, stacklevel=2)
        fig.savefig(path, **kw)
        written.append(path)
    return written


# --------------------------------------------------------------------------
def _selftest() -> int:
    import tempfile
    info = use_style("nature", lang="en")
    print("[use_style]", {k: info[k] for k in ("journal", "picked", "substituted",
                                               "base_pt", "min_pt")})
    print("[fonts]    ", info["fonts"])
    w, h = figure_size("nature", cols=2, ratio=0.42)
    print(f"[size]      {w} x {h} in")
    fig, axes = plt.subplots(1, 2, figsize=(w, h))
    rng = np.random.default_rng(0)
    ns = box_strip(axes[0], {"ctrl": rng.normal(0, 1, 12),
                             "treat": rng.normal(1.2, 1, 11)})
    axes[0].set_xlabel("condition")
    axes[0].set_ylabel("signal (a.u.)")
    sig_bracket(axes[0], 0, 1, np.max(np.concatenate([[3]])), "p=0.004")
    print("[box_strip] n per group =", ns)
    x = np.linspace(0, 6, 60)
    for i, k in enumerate([1.0, 1.5, 2.0]):
        axes[1].plot(x, np.sin(k * x), label=f"k={k}", color=categorical(3)[i])
    axes[1].set_xlabel("position (bp)")
    axes[1].set_ylabel("score")
    axes[1].legend(loc="lower left", ncol=3)
    finalize(fig)
    labs = panel_labels(fig)
    fig.canvas.draw()
    inside = all(0 <= t.get_window_extent(fig.canvas.get_renderer()).y1 <= fig.bbox.height
                 for t in labs)
    print(f"[panels]    {[t.get_text() for t in labs]} inside_canvas={inside}")
    assert inside, "panel labels ended up off-canvas"
    try:
        from figcheck import audit, report
        print("[figcheck]")
        report(audit(fig, min_pt=info["min_pt"]))
    except ImportError:
        pass
    out = save(fig, os.path.join(tempfile.gettempdir(), "scifig_selftest"),
               formats=("pdf", "png"), dpi=200,
               provenance={"data": "synthetic rng(0)", "script": __file__})
    print("[save]     ", out)
    zh = use_style("default", lang="zh")
    print("[zh fonts] ", zh["fonts"], "| cjk =", zh["cjk"])
    plt.close(fig)
    print("selftest OK")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_selftest() if "--selftest" in sys.argv else _selftest())
