# Changelog

Versions are per plugin and recorded in `.claude-plugin/marketplace.json` and each
plugin's `plugin.json`. Earlier history is in the git log.

## scifig 1.2.0 — 2026-09-14

- `figcheck.audit` detects a truncated baseline on horizontal bars (`ax.barh`), not only
  vertical ones, and reports bars on a log axis as a warning instead of a false failure.
- `figstyle.panel_labels` no longer stamps a panel letter on colorbar axes.
- `figstyle.finalize` names the likely cause when constrained layout cannot adopt a
  colorbar added before the figure had a layout engine; the skill, recipes, and review
  checklist now create such figures with `layout="constrained"`.
- `figcheck.py --cvd` on a vector file without `pymupdf` reports a warning instead of a
  traceback; demo and CVD scratch files go to the platform temp directory instead of `/tmp`.
- `figstyle.py` rejects unknown command-line arguments with a usage message.
- Both command lines replace characters a legacy console encoding (cp1252, GBK) cannot
  print instead of crashing with a traceback.
- Skill text lists all ten deterministic checks that `audit` performs.

## rigor 1.3.0

- Adds `confirming-parameters` for values inherited from earlier rounds, prior runs, or
  notes. Plugin description now names all four guardrails.

## Repository

- Tests read files as UTF-8 explicitly and CI also runs on Windows.
