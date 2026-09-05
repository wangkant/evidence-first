"""
scifig :: figcheck.py — deterministic post-render checks + CVD/grayscale simulation

Division of labour (important — don't run only half of it)
---------------------------------------------------------
- **This script** catches only what can be **computed**: missing glyphs, text out
  of bounds, colliding ticks, type below the journal floor, a continuous color
  mapping with no colorbar, rainbow/jet colormaps, a legend covering data points,
  a truncated bar baseline, missing axis labels, and more categorical colors than
  are distinguishable. None of these need eyes; arithmetic settles them.
- **Your eyes** catch what cannot be computed: does the figure make its point? Is
  the whitespace balanced? Are the panel weights right? That is why ``preview()``
  renders a PNG that you must **actually look at** with the Read tool. Checklist
  in references/review.md.

Both, or the figure is not done.

Usage
-----
    from figcheck import audit, report, preview, cvd_preview

    issues = audit(fig, min_pt=5)          # journal type-size floor
    report(issues)                          # prints; returns PASS/WARN/FAIL
    png = preview(fig, "figs/_check.png")   # then Read this file
    cvd_preview(png)                        # red-green CVD + grayscale versions

CLI
---
    python figcheck.py demo                 # demo on a deliberately broken figure
    python figcheck.py figs/fig1.pdf        # check a written file (size/DPI/font embedding)
    python figcheck.py figs/fig1.png --cvd  # write color-vision simulations
"""
from __future__ import annotations

import argparse

import logging
import os
import sys
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.text as mtext
import numpy as np

__all__ = ["audit", "report", "preview", "cvd_preview", "check_file"]

SEVERITY = {"INFO": 0, "WARN": 1, "FAIL": 2}
_GLYPH_MARKERS = ("missing from", "Glyph", "findfont")
# Rainbow colormaps: hue is not monotonic in the value and lightness is not
# uniform, so they manufacture boundaries and peaks that are not in the data.
# See Borland & Taylor 2007, "Rainbow Color Map (Still) Considered Harmful".
_RAINBOW = {"jet", "rainbow", "gist_rainbow", "hsv", "nipy_spectral",
            "gist_ncar", "flag", "prism", "brg", "CMRmap", "gist_stern"}
_MARGINAL = {"turbo", "gist_earth", "terrain", "ocean"}


# --------------------------------------------------------------------------
# Intercepting render-time warnings (missing glyphs)
# --------------------------------------------------------------------------
class _GlyphLog(logging.Handler):
    def __init__(self):
        super().__init__()
        self.msgs: list[str] = []

    def emit(self, record):
        m = record.getMessage()
        if any(k in m for k in _GLYPH_MARKERS):
            self.msgs.append(m)


def _draw_collect(fig) -> list[str]:
    """Render once, collecting missing-glyph warnings from both channels.

    matplotlib versions report differently (older via warnings, newer via
    logging), so both must be hooked or the check leaks. This also readies the
    renderer for the bounding-box measurements below.

    Uses ``canvas.draw()`` rather than ``savefig(dpi=...)``: savefig re-runs
    constrained layout at the **output** dpi while fig.bbox is still at
    figure.dpi, and the mismatch makes the out-of-bounds check measure negative
    coordinates and report false positives. draw() triggers glyph warnings too.
    """
    h = _GlyphLog()
    lg = logging.getLogger("matplotlib")
    prev = lg.level
    lg.setLevel(logging.WARNING)
    lg.addHandler(h)
    got: list[str] = []
    try:
        with warnings.catch_warnings(record=True) as wl:
            warnings.simplefilter("always")
            fig.canvas.draw()
        got += [str(w.message) for w in wl
                if any(k in str(w.message) for k in _GLYPH_MARKERS)]
    finally:
        lg.removeHandler(h)
        lg.setLevel(prev)
    got += h.msgs
    return list(dict.fromkeys(got))


def _renderer(fig):
    try:
        return fig.canvas.get_renderer()
    except AttributeError:
        fig.canvas.draw()
        return fig.canvas.get_renderer()


def _data_axes(fig):
    """The actual data subplots (colorbar axes excluded — having no xlabel is normal there)."""
    out = []
    for ax in fig.axes:
        if ax.get_subplotspec() is None and not ax.get_position().width:
            continue
        if getattr(ax, "_colorbar", None) is not None:
            continue
        # a colorbar's host axes carries _colorbar_info in mpl, or is extremely narrow
        if getattr(ax, "_colorbar_info", None) is not None:
            continue
        out.append(ax)
    return out


# --------------------------------------------------------------------------
def audit(fig, min_pt: float = 6.0, max_categorical: int = 8,
          clip_tol: float = 2.0, overlap_tol: float = 1.0) -> list[tuple[str, str]]:
    """
    Run deterministic checks on a Figure; returns [(severity, message), ...].
    Non-destructive: it renders and measures, it does not modify the figure.
    """
    issues: list[tuple[str, str]] = []
    glyph = _draw_collect(fig)
    if glyph:
        issues.append(("FAIL",
                       f"missing glyphs — the figure will contain boxes or garbage: "
                       f"{' | '.join(glyph[:2])[:200]}. For CJK figures call "
                       "use_style(lang='zh') first; if it is only the minus sign, set "
                       "axes.unicode_minus=False."))

    r = _renderer(fig)
    W, H = float(fig.bbox.width), float(fig.bbox.height)
    axes = _data_axes(fig)

    # --- Type-size floor: journals measure printed type and bounce anything below
    small = {}
    for t in fig.findobj(mtext.Text):
        try:
            if not (t.get_visible() and t.get_text().strip()):
                continue
            fs = float(t.get_fontsize())
        except Exception:
            continue
        if fs < min_pt - 1e-6:
            small.setdefault(round(fs, 1), t.get_text().strip()[:18])
    if small:
        issues.append(("FAIL",
                       f"type below the {min_pt} pt floor: {small}. Do not shrink type "
                       "to make room — reduce the tick count, shorten labels, or "
                       "enlarge figsize."))

    # --- Text out of bounds (tick labels skipped: they have their own overlap
    #     check and legitimately sit at the edge)
    tick_ids = set()
    for ax in fig.axes:
        for tl in (*ax.get_xticklabels(), *ax.get_yticklabels(),
                   *ax.get_xticklabels(minor=True), *ax.get_yticklabels(minor=True)):
            tick_ids.add(id(tl))
    clipped = []
    for t in fig.findobj(mtext.Text):
        if id(t) in tick_ids:
            continue
        try:
            if not (t.get_visible() and t.get_text().strip()):
                continue
            bb = t.get_window_extent(r)
        except Exception:
            continue
        if (bb.x0 < -clip_tol or bb.y0 < -clip_tol
                or bb.x1 > W + clip_tol or bb.y1 > H + clip_tol):
            clipped.append(t.get_text().strip().replace("\n", " ")[:22])
    if clipped:
        issues.append(("WARN",
                       f"text extends past the canvas and will be clipped: "
                       f"{list(dict.fromkeys(clipped))[:5]}. Run figstyle.finalize(fig); "
                       "if it still overflows, shorten the text or widen figsize "
                       "(do not paper over it with bbox_inches='tight' — that changes "
                       "the final size)."))

    # --- Colliding tick labels ---------------------------------------------
    nover = 0
    for ax in axes:
        if _overlap(ax.get_xticklabels(), r, "x", overlap_tol) or \
           _overlap(ax.get_yticklabels(), r, "y", overlap_tol):
            nover += 1
    if nover:
        issues.append(("WARN", f"{nover} subplot(s) have colliding tick labels. For x, "
                               "use tick_params(axis='x', rotation=30) or fewer ticks; "
                               "for y, make the subplot taller or use MaxNLocator(4)."))

    # --- Missing axis labels (readers cannot tell what quantity or unit) -----
    # Labelling a facet grid once with fig.supxlabel/supylabel is **correct** and
    # must not warn.
    supx = bool(getattr(getattr(fig, "_supxlabel", None), "get_text", str)()
                if getattr(fig, "_supxlabel", None) is not None else "")
    supy = bool(getattr(getattr(fig, "_supylabel", None), "get_text", str)()
                if getattr(fig, "_supylabel", None) is not None else "")
    nolabel = [i for i, ax in enumerate(axes)
               if ax.axison
               and ((not supx and _needs_axis_label(ax, "x")
                     and not ax.get_xlabel().strip())
                    or (not supy and _needs_axis_label(ax, "y")
                        and not ax.get_ylabel().strip()))]
    if nolabel:
        shared = any(ax.get_subplotspec() is not None for ax in axes) and len(axes) > 1
        sev = "WARN" if shared else "FAIL"
        issues.append((sev, f"subplot(s) {nolabel} have no x or y axis label. Axis labels "
                            "should read 'quantity (unit)'; a facet grid may label the "
                            "whole set once with fig.supxlabel/supylabel."))

    # --- Continuous color mapping with no colorbar / rainbow colormap -------
    for m in _mappables(fig):
        name = getattr(m.get_cmap(), "name", "")
        if name in _RAINBOW:
            issues.append(("FAIL", f"rainbow colormap '{name}': hue is not monotonic in "
                                   "the value and lightness is not uniform, so it "
                                   "manufactures boundaries that are not in the data. "
                                   "Use viridis/cividis for sequential data, RdBu_r when "
                                   "zero is meaningful."))
        elif name in _MARGINAL:
            issues.append(("WARN", f"colormap '{name}' is not CVD-safe and is hard to "
                                   "read in grayscale. Unless it carries topographic "
                                   "meaning, switch to viridis/cividis."))
        # A discrete ListedColormap (the "which class is this row" annotation bar
        # kind) is adequately explained by a legend and should not be forced to
        # carry a colorbar — counting it would drown out genuinely missing
        # colorbars on continuous mappings.
        cm = m.get_cmap()
        categorical_cmap = (isinstance(cm, mpl.colors.ListedColormap)
                            and getattr(cm, "N", 256) <= 12)
        if not categorical_cmap and getattr(m, "colorbar", None) is None:
            issues.append(("WARN", "continuous color mapping with no colorbar: readers "
                                   "cannot tell what the shading corresponds to. "
                                   "fig.colorbar(m, ax=..., label='quantity (unit)')."))

    # --- Too many categorical colors ----------------------------------------
    for i, ax in enumerate(axes):
        cols = {_rgba(l.get_color()) for l in ax.get_lines() if l.get_visible()}
        if len(cols) > max_categorical:
            issues.append(("WARN", f"subplot {i} uses {len(cols)} line colors, beyond the "
                                   f"~{max_categorical} people distinguish reliably. Use "
                                   "small multiples, or color only 2-3 lines and draw the "
                                   "rest in pale gray."))

    # --- Truncated bar baseline (the classic deception) ---------------------
    for i, ax in enumerate(axes):
        bars = [p for c in ax.containers for p in c
                if isinstance(p, mpl.patches.Rectangle)] if ax.containers else []
        if len(bars) < 2:
            continue
        y0 = ax.get_ylim()[0]
        bases = {round(float(b.get_y()), 9) for b in bars}
        if bases == {0.0} and y0 > 0:
            issues.append(("FAIL", f"subplot {i} draws bars from 0 but the y axis starts "
                                   f"at {y0:g}, so bar length is no longer proportional to "
                                   "the value — this inflates a tiny difference into a "
                                   "huge one. Set ax.set_ylim(bottom=0), or use a dot plot "
                                   "or difference plot to show small differences."))

    # --- Legend covering the data -------------------------------------------
    for i, ax in enumerate(axes):
        leg = ax.get_legend()
        if leg is None:
            continue
        try:
            lb = leg.get_window_extent(r)
        except Exception:
            continue
        hidden = _points_under(ax, lb, r)
        if hidden > 0.02:
            issues.append(("WARN", f"subplot {i}'s legend covers about {hidden:.0%} of the "
                                   "data points. Move it outside: ax.legend(loc='upper "
                                   "left', bbox_to_anchor=(1.01, 1)), or label the series "
                                   "next to the curves (dropping the legend saves the "
                                   "reader the back-and-forth)."))

    return issues


def _needs_axis_label(ax, which: str) -> bool:
    """
    Whether this axis ought to carry a label.

    Inner subplots of a shared axis (the ones whose tick labels are hidden) do not
    need their own axis label — the outer ring carries it for the group. Treating
    that as a defect produces a flood of false positives, and a checker that
    always cries wolf is not a checker.
    """
    shared = ax.get_shared_x_axes() if which == "x" else ax.get_shared_y_axes()
    try:
        n_sib = len(list(shared.get_siblings(ax)))
    except Exception:
        n_sib = 1
    if n_sib <= 1:
        return True
    labels = ax.get_xticklabels() if which == "x" else ax.get_yticklabels()
    return any(t.get_visible() for t in labels)


def _rgba(c):
    try:
        return tuple(round(v, 3) for v in mpl.colors.to_rgba(c))
    except Exception:
        return str(c)


def _mappables(fig):
    """
    Every color-mapped artist in the figure, **excluding the color strip a
    colorbar draws for itself**.

    A colorbar is internally a mappable, and of course it has no colorbar of its
    own — without this exclusion, every colorbar you add produces one more false
    "missing colorbar" alarm.
    """
    found = []
    for ax in fig.axes:
        found += list(ax.images) + [c for c in ax.collections
                                    if getattr(c, "get_array", lambda: None)() is not None]
    cbar_axes = {m.colorbar.ax for m in found if getattr(m, "colorbar", None) is not None}
    return [m for m in found if getattr(m, "axes", None) not in cbar_axes]


def _overlap(labels, r, axis, tol) -> bool:
    bs = []
    for l in labels:
        try:
            if l.get_visible() and l.get_text().strip():
                bs.append(l.get_window_extent(r))
        except Exception:
            continue
    if len(bs) < 2:
        return False
    if axis == "x":
        bs.sort(key=lambda b: b.x0)
        return any(a.x1 - b.x0 > tol for a, b in zip(bs, bs[1:]))
    bs.sort(key=lambda b: b.y0)
    return any(a.y1 - b.y0 > tol for a, b in zip(bs, bs[1:]))


def _points_under(ax, box, r) -> float:
    """Fraction of data points falling inside box. Lines contribute vertices, scatters offsets."""
    pts = []
    for l in ax.get_lines():
        if not l.get_visible():
            continue
        xy = l.get_xydata()
        if len(xy):
            pts.append(ax.transData.transform(xy))
    for c in ax.collections:
        try:
            off = c.get_offsets()
            if off is not None and len(off):
                pts.append(ax.transData.transform(np.asarray(off)))
        except Exception:
            continue
    if not pts:
        return 0.0
    P = np.vstack(pts)
    P = P[np.isfinite(P).all(axis=1)]
    if not P.size:
        return 0.0
    inside = ((P[:, 0] >= box.x0) & (P[:, 0] <= box.x1) &
              (P[:, 1] >= box.y0) & (P[:, 1] <= box.y1))
    return float(inside.mean())


# --------------------------------------------------------------------------
def report(issues, verbose: bool = True) -> str:
    if not issues:
        if verbose:
            print("  [PASS] no deterministic defects.")
            print("  >>> Not done yet: render a PNG with preview() and look at it "
                  "yourself with Read (checklist in references/review.md).")
        return "PASS"
    verdict = {2: "FAIL", 1: "WARN", 0: "INFO"}[max(SEVERITY[s] for s, _ in issues)]
    if verbose:
        for sev, msg in sorted(issues, key=lambda x: -SEVERITY[x[0]]):
            print(f"  [{sev}] {msg}")
        print(f"  >>> verdict: {verdict}")
    return verdict


def preview(fig_or_path, out: str = "_preview.png", dpi: int = 160) -> str:
    """Render a PNG for you to Read. A vector PDF cannot show pixel-level occlusion; rasterize first."""
    if hasattr(fig_or_path, "savefig"):
        os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
        fig_or_path.savefig(out, dpi=dpi)
        return out
    p = str(fig_or_path)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    if os.path.splitext(p)[1].lower() in {".png", ".tif", ".tiff", ".jpg", ".jpeg"}:
        return p
    try:
        import fitz
    except ImportError as e:
        raise RuntimeError("rendering a PDF to a preview needs pymupdf; better still, "
                           "pass the Figure object directly and look at it before "
                           "exporting.") from e
    doc = fitz.open(p)
    doc[0].get_pixmap(dpi=dpi).save(out)
    doc.close()
    return out


# Dichromacy simulation matrices (the linear approximation of Viénot, Brettel &
# Mollon 1999, applied in linear sRGB).
_CVD = {
    "deuteranopia": np.array([[0.625, 0.375, 0.0],
                              [0.700, 0.300, 0.0],
                              [0.0,   0.300, 0.700]]),
    "protanopia":   np.array([[0.567, 0.433, 0.0],
                              [0.558, 0.442, 0.0],
                              [0.0,   0.242, 0.758]]),
    "tritanopia":   np.array([[0.950, 0.050, 0.0],
                              [0.0,   0.433, 0.567],
                              [0.0,   0.475, 0.525]]),
}


def cvd_preview(png: str, kinds=("deuteranopia", "grayscale")) -> list[str]:
    """
    Write color-vision and grayscale simulations. About 8% of men have a red-green
    color vision deficiency, and some of your reviewers are among them; the
    grayscale version corresponds to being printed in black and white. **Check
    whether the same conclusion is readable in both** — if not, the information is
    riding entirely on hue and needs a redundant encoding (shape, line style,
    direct labeling).
    """
    from PIL import Image
    img = np.asarray(Image.open(png).convert("RGB"), dtype=np.float64) / 255.0
    lin = np.where(img <= 0.04045, img / 12.92, ((img + 0.055) / 1.055) ** 2.4)
    outs = []
    for k in kinds:
        if k == "grayscale":
            y = lin @ np.array([0.2126, 0.7152, 0.0722])
            sim = np.repeat(y[:, :, None], 3, axis=2)
        else:
            sim = lin @ _CVD[k].T
        sim = np.clip(sim, 0, 1)
        srgb = np.where(sim <= 0.0031308, sim * 12.92,
                        1.055 * sim ** (1 / 2.4) - 0.055)
        path = f"{os.path.splitext(png)[0]}_{k}.png"
        Image.fromarray((np.clip(srgb, 0, 1) * 255).astype(np.uint8)).save(path)
        outs.append(path)
    return outs


def check_file(path: str, min_dpi: int = 300,
               expect_inches: tuple[float, float] | None = None) -> list[tuple[str, str]]:
    """Check a figure **already written to disk**: format, raster resolution, vector size, font embedding."""
    if not os.path.isfile(path):
        return [("FAIL", f"figure file does not exist: {path}")]
    try:
        return _check_file(path, min_dpi, expect_inches)
    except (OSError, ValueError, EOFError, TypeError, KeyError, IndexError) as exc:
        return [("FAIL", f"cannot inspect figure {path}: {exc}")]


def _size_issues(width, height, expected):
    if expected is None:
        return []
    return [("WARN", f"{axis} {actual:.2f} in ≠ target {target:g} in. "
                     "Fix figsize and re-export; rescaling also changes type size.")
            for axis, actual, target in zip(("width", "height"), (width, height), expected)
            if abs(actual - target) > 0.06]


def _check_file(path, min_dpi, expect_inches):
    issues = []
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext in ("jpg", "jpeg"):
        issues.append(("FAIL", "JPEG data figure: compression artifacts leave ringing "
                               "along line edges and journals reject it. Use PDF/SVG "
                               "(vector) or PNG/TIFF (raster)."))
    if ext in ("png", "tif", "tiff", "jpg", "jpeg"):
        from PIL import Image
        with Image.open(path) as im:
            im.load()  # Detect truncated/corrupt pixel data, not just a readable header.
            raw_dpi = im.info.get("dpi")
            if raw_dpi is None:
                issues.append(("WARN", "DPI metadata is absent; physical size and resolution are unknown."))
            else:
                dx, dy = raw_dpi if isinstance(raw_dpi, (tuple, list)) else (raw_dpi, raw_dpi)
                if not all(np.isfinite(d) and d > 0 for d in (dx, dy)):
                    return issues + [("FAIL", f"invalid DPI metadata: {raw_dpi}")]
                w, h = im.width / dx, im.height / dy
                issues.append(("INFO", f"{ext.upper()} {im.width}x{im.height} px @ "
                                       f"{dx:g}x{dy:g} dpi → {w:.2f} x {h:.2f} in"))
                # PNG's pixels-per-metre encoding rounds 300 dpi to about 299.9994.
                if min(dx, dy) < min_dpi - 0.01:
                    issues.append(("WARN", f"{dx:g}x{dy:g} dpi is below {min_dpi}. "
                                           "Export at the required resolution or use vector output."))
                issues.extend(_size_issues(w, h, expect_inches))
    elif ext == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return issues + [("WARN", "PDF checks skipped: install pypdf to check size and font embedding.")]
        from pypdf.errors import PdfReadError
        try:
            rd = PdfReader(path)
            if not rd.pages:
                return [("FAIL", "PDF contains no pages.")]
        except PdfReadError as exc:
            return [("FAIL", f"cannot inspect PDF: {exc}")]
        if len(rd.pages) > 1:
            issues.append(("WARN", "Multi-page PDF: only the first page is checked."))
        box = rd.pages[0].mediabox
        w, h = float(box.width) / 72, float(box.height) / 72
        issues.append(("INFO", f"PDF {w:.2f} x {h:.2f} in"))
        issues.extend(_size_issues(w, h, expect_inches))
        # Font embedding: the presence of /FontFile* means embedded. A name with an
        # 'ABCDEF+' prefix is the standard notation for **a subset that IS
        # embedded**, not for "missing" — don't be fooled by the prefix.
        fonts, embedded = set(), set()
        res = rd.pages[0].get("/Resources", {})
        fdict = res.get("/Font", {}) if hasattr(res, "get") else {}
        try:
            for k in list(fdict.keys()):
                f = fdict[k].get_object()
                nm = str(f.get("/BaseFont", "?"))
                fonts.add(nm)
                desc = f.get("/FontDescriptor")
                stack = [f]
                if "/DescendantFonts" in f:
                    stack += [d.get_object() for d in f["/DescendantFonts"]]
                for s in stack:
                    d = s.get("/FontDescriptor")
                    if d and any(x in d.get_object()
                                 for x in ("/FontFile", "/FontFile2", "/FontFile3")):
                        embedded.add(nm)
                del desc
        except Exception as e:
            issues.append(("WARN", f"font check skipped: {e}"))
        if fonts:
            missing = fonts - embedded
            issues.append(("INFO", f"fonts {sorted(n.split('+')[-1] for n in fonts)}"))
            if missing:
                issues.append(("WARN", f"not embedded: {sorted(missing)}. Set "
                                       "rcParams['pdf.fonttype']=42 and re-export."))
    else:
        issues.append(("WARN", f"unsupported file format for inspection: .{ext}. "
                               "Use audit(fig) before export and inspect a PNG preview."))
    return issues


# --------------------------------------------------------------------------
def _demo() -> int:
    """Deliberately draw a figure with five classes of defect, to verify the checks fire."""
    rng = np.random.default_rng(1)
    fig, axes = plt.subplots(1, 2, figsize=(5.0, 2.2))
    ax = axes[0]
    vals = np.array([10.1, 10.4, 10.2, 10.6])
    ax.bar(range(4), vals)
    ax.set_ylim(9.8, 10.8)                              # truncated baseline → FAIL
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"very_long_condition_{i}" for i in range(4)])  # overlap
    ax.set_title("A deliberately overlong title that runs past the canvas edge")
    ax.tick_params(labelsize=4)                          # type too small → FAIL
    im = axes[1].imshow(rng.random((8, 8)), cmap="jet")  # rainbow + no colorbar
    del im
    x = np.linspace(0, 1, 40)
    for i in range(3):
        axes[1].plot([], [], label=f"s{i}")
    axes[1].legend(loc="center")
    del x
    print("=== figcheck demo (this figure is broken on purpose) ===")
    report(audit(fig, min_pt=6))
    out = preview(fig, "/tmp/figcheck_demo.png", dpi=120)
    print(f"preview: {out}")
    print(f"CVD simulations: {cvd_preview(out)}")
    plt.close(fig)
    return 0


def _cli() -> int:
    p = argparse.ArgumentParser(description="scifig figure QC")
    p.add_argument("target", nargs="?", default="demo", help="image path, or 'demo'")
    p.add_argument("--cvd", action="store_true", help="write color-vision/grayscale simulations")
    p.add_argument("--min-dpi", type=int, default=300)
    p.add_argument("--strict", action="store_true", help="also exit nonzero on WARN, including skipped checks")
    p.add_argument("--inches", type=float, nargs=2, default=None,
                   metavar=("W", "H"), help="expected final size in inches")
    a = p.parse_args()
    if a.min_dpi <= 0:
        p.error("--min-dpi must be positive")
    if a.inches and not all(np.isfinite(v) and v > 0 for v in a.inches):
        p.error("--inches requires finite positive width and height")
    if a.target == "demo":
        return _demo()
    verdict = report(check_file(a.target, a.min_dpi, tuple(a.inches) if a.inches else None))
    if verdict == "FAIL":
        return 1
    if a.cvd:
        print("CVD simulations:", cvd_preview(preview(a.target, "/tmp/_cvd_src.png")))
    return int(a.strict and verdict == "WARN")


if __name__ == "__main__":
    sys.exit(_cli())
