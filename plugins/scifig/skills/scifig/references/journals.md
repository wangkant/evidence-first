# Journal specs and typesetting

Contents
1. [Size and type size](#1-size-and-type-size)
2. [Format and resolution](#2-format-and-resolution)
3. [Fonts](#3-fonts)
4. [Panel labels](#4-panel-labels)
5. [Captions](#5-captions)
6. [CJK typesetting](#6-cjk-typesetting)
7. [Pre-submission checklist](#7-pre-submission-checklist)

---

## 1. Size and type size

`figstyle.JOURNALS` stores each journal's column widths in inches;
`figure_size(journal, cols=1|1.5|2)` returns the final size directly.

⚠️ **This table is a working default, not an authoritative source.** Journals revise their
guidelines. Before submitting, check the current figure guideline for your target journal.
Any number you put in the manuscript or a response to reviewers needs a locator — see the
sibling skill `sourcing-claims`.

| Journal | 1 col | 1.5 col | 2 col | Body pt | Min pt | Font |
|---|---|---|---|---|---|---|
| Nature | 3.50 | 4.76 | 7.20 | 7 pt | 5 pt | Helvetica/Arial |
| Science | 2.24 | 3.74 | 4.76 | 7 pt | 6 pt | Helvetica |
| Cell | 3.35 | 4.49 | 6.85 | 7 pt | 6 pt | Arial |
| PNAS | 3.42 | 4.49 | 7.00 | 8 pt | 6 pt | Helvetica |
| PLOS | 2.63 | 5.20 | 7.50 | 8 pt | 8 pt | Arial |
| eLife | 3.35 | 4.72 | 6.85 | 8 pt | 6 pt | Arial |
| NAR | 3.39 | 4.72 | 7.01 | 8 pt | 6 pt | Arial |
| BMC / Genome Biology | 3.35 | 4.72 | 6.69 | 8 pt | 6 pt | Arial |
| Elsevier titles | 3.54 | 5.51 | 7.48 | 8 pt | 7 pt | Arial |
| IEEE | 3.50 | — | 7.16 | 8 pt | 6 pt | Times |
| ACM | 3.33 | — | 7.00 | 8 pt | 6 pt | Times |
| NeurIPS / ICML | 5.50 | — | 5.50 | 8 pt | 7 pt | Times |
| Thesis | 4.50 | 5.50 | 6.30 | 9 pt | 8 pt | Times / serif |
| Slides | 5.00 | 7.50 | 10.0 | 14 pt | 12 pt | sans-serif |

**Render at the final size and never rescale afterwards.** matplotlib type sizes are
absolute points: a 7.2 in figure scaled to 3.5 in inside Word turns 8 pt ticks into 3.9 pt,
below every journal's floor. `figcheck.audit(fig, min_pt=...)` checks type size;
`figcheck.check_file(pdf, expect_inches=...)` checks the size of what actually landed on disk.

Height: most journals allow around 9 in of live area (Nature about 9.7 in). `figure_size`
warns when you exceed it.

---

## 2. Format and resolution

| Content | Format | Notes |
|---|---|---|
| Lines, scatter, bars, boxplots, modest-grid heatmaps | **PDF or EPS/SVG** | Vector: sharp at any zoom, text searchable and tweakable in layout |
| Micrographs, gels, photographs | TIFF or PNG, ≥300 dpi | |
| Pure line art as raster (last resort) | PNG 600 dpi | |
| Huge point clouds / high-res heatmaps | Hybrid: raster data layer, vector text layer | `ax.set_rasterized(True)` rasterizes only the data layer |

**Never use JPEG for data figures**: lossy compression leaves ringing artifacts along
high-contrast edges, and journal PDF preflight will bounce it.

Font embedding: `figstyle.use_style()` already sets `pdf.fonttype=42` (TrueType subset
embedding). When checking, note that a six-letter prefix like `ABCDEF+NimbusSans` in the
PDF is the standard notation for **a subset that IS embedded**, not for "not embedded" —
counting `/FontFile*` entries is the actual criterion, and that is what
`figcheck.check_file` uses.

`svg.fonttype='none'` keeps text as text in the SVG (not converted to outlines), so it
stays editable in Illustrator — but the opening machine needs the same font installed. To
hand the typesetter something that cannot go wrong, give them the PDF.

---

## 3. Fonts

Journals almost always want Helvetica / Arial (life sciences) or Times (engineering, CS).
A Linux machine typically has none of them. `figstyle.resolve_font()` falls back to a
**metric-compatible** clone:

| What the journal wants | Metric-compatible substitute | Relationship |
|---|---|---|
| Helvetica | Nimbus Sans (URW) / TeX Gyre Heros | Identical advance widths and heights, so layout does not shift |
| Arial | Liberation Sans / Arimo | Google's metric-compatible Arial replacements |
| Times New Roman | Nimbus Roman / Liberation Serif / Tinos | Same idea |

Metric-compatible means every character occupies the same box after substitution, so the
figure's layout does not move. The look differs slightly, but far less than silently
falling back to DejaVu Sans, which is noticeably wider.

`substituted=True` in the dict returned by `use_style()` is the paper trail for "the
original font was not used" — **print it**. If a journal hard-requires the original font,
re-render on a machine that has it.

---

## 4. Panel labels

`figstyle.panel_labels(fig, style=...)`:

- `style='nature'` → `a b c` (lowercase, no parentheses; Nature/Cell/Science convention)
- `style='ieee'` → `(a) (b) (c)` (IEEE/ACM convention)
- `style='upper'` → `A B C` (some journals)

Label positions are computed uniformly in **figure coordinates**, so labels in a column
are naturally left-aligned and labels in a row are naturally top-aligned. Hand-written
`ax.text` is the most common source of ragged panel labels: each axes has a different data
range, so the same `ax.text(-0.1, 1.05, ...)` lands at a different physical position in
each subplot.

---

## 5. Captions

A caption must be readable independently of the main text:

```
Figure 3. <supported conclusion or descriptive exploratory title>.
(a) <what is plotted>. Points = <what one row is>, n = <n per group>.
Error bars = <SD / SEM / 95% CI — say which>.
Statistics = <test and correction, if performed>; identify sampling unit and pairing.
Scale bar = <required for micrographs>. Data source: <file / pipeline>.
```

Include uncertainty and statistics only when actually computed. **State the error type.**
SD describes spread. SEM = SD/√n assumes independent observations; a normal-approximation
95% CI for a mean is mean ±1.96 SEM, but that approximation is not universal. State the
CI method and preserve pairing or clustering. Do not fabricate uncertainty from a single
summary value or add an unrequested significance test to complete the caption.

Annotating **exact p values** beats stars: stars discard precision, and journals do not
agree on what `*` means.

---

## 6. CJK typesetting

The root cause of CJK text rendering as boxes in matplotlib: the default font contains no
CJK glyphs.

```python
info = use_style("thesis", lang="zh")
print(info["fonts"])   # ['Nimbus Sans', 'Droid Sans Fallback', 'DejaVu Sans']
```

**The key mechanism (verified on mpl 3.10/3.11):** per-glyph fallback only takes effect
when `font.family` is given a list of concrete font names. Writing
`font.family='sans-serif'` plus `font.sans-serif=[...]` does **not** fall back — CJK stays
boxed. Most online "CJK shows as boxes" tutorials tell you to set a single CJK font, which
sidesteps the trap at the cost of rendering Latin letters and math symbols in the CJK font
too, which looks bad. `figstyle` uses the former, so Latin/Greek/math come from the Western
font and CJK glyphs come from the CJK font in the same string.

Journals that want "serif body text with Times numerals" are served by
`use_style('thesis', lang='zh')`, which uses the serif chain (Nimbus Roman + Noto Serif CJK
/ SimSun).

Boxed minus sign: `axes.unicode_minus` stays True when fallback is available (U+2212 comes
from the Western font); matplotlib < 3.6 has no per-glyph fallback, so `use_style` sets it
to False automatically.

If fonts are missing, installing one is enough:

```bash
conda install -c conda-forge font-ttf-source-han-sans   # or
apt install fonts-noto-cjk fonts-droid-fallback
python -c "import matplotlib.font_manager as fm; fm._load_fontmanager(try_read_cache=False)"
```

---

## 7. Pre-submission checklist

- [ ] Size equals the target column width, and **nothing was rescaled after export**
- [ ] Smallest type ≥ the journal floor (`figcheck.audit(fig, min_pt=...)` passes)
- [ ] Vector format (unless photograph/micrograph); not JPEG
- [ ] Fonts embedded (`figcheck.check_file`'s `/FontFile` criterion)
- [ ] Palette CVD-safe, with a redundant encoding beyond color; grayscale still readable
- [ ] Every continuous color mapping has a colorbar labeled with quantity and unit
- [ ] Every axis has a label and a unit
- [ ] Error-bar type, n, test, and correction all stated in the caption
- [ ] Panel-label style matches journal convention and the labels are aligned
- [ ] Every number on the figure was computed from the data (not typed in), and the script
      asserts the claim
- [ ] You have read the rendered PNG with your own eyes (not merely run the checker)
