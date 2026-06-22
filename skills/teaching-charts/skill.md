# teaching:charts

## When to invoke

Trigger on: "make a chart"; "plot/graph this data"; "FRED/BEA/Census/BLS chart"; "time
series"/"bar"/"scatter"/"dot-plot"/"box-whisker"; "an AER table from these results"; or any
need for a figure/table caption. Always use `chart_lib` + the house style; pull data via
`datasources`/`from_registry`. For schematic theory diagrams, use `teaching:diagrams`.

---

Empirical charts and tables from data, in Bieri house style (Palatino/Pagella, Heros).
Dual-target PNG (pptx) / PDF (LaTeX/Beamer); caption + table toggle; AER conventions. Also
hosts the shared caption/standards layer used by `teaching:diagrams` and `teaching:compose-slides`.

---

## Bundled resources

- `scripts/bieri.mplstyle` — matplotlib house style (Pagella serif, Heros sans, palette,
  dropped top/right spines, light y-grid).
- `scripts/chart_lib.py` — `timeseries`, `bar`, `scatter` (incl. `dotplot=True`), `box`; each
  takes `target` (`png` pptx · `pdf`/`pgf` LaTeX) and `caption_mode` (`off`/`host`/`baked`).
  Auto-registers tex-gyre fonts. `sankey()` documents the plotly path (needs `plotly`+`kaleido`).
- `scripts/datasources.py` + `series_registry.yaml` — cache-first FRED/BEA/Census/BLS adapters
  → tidy `date|value|series_id|label|source` frames with provenance. `from_registry("housing_starts")`.
- `scripts/figures.py` — caption layer: `pptx_caption`, `latex_figure`, `latex_table` (booktabs,
  AER: leading-zero decimals, ≤9-col warning, source-note last), `dump_json` (→ captions.json).
- `scripts/captions.yaml` — author captions ONCE; reused across pptx/Beamer/paper.
- `scripts/bieri-preamble.tex` — AER math macros for papers/Beamer.
- `references/house-style.md` — adopted AER standard (canonical). `references/USER_GUIDE.md` +
  `process_overview.png` — the figure-system manual.

## Workflow

```python
import chart_lib as C
from datasources import from_registry
df = from_registry("housing_starts")                         # cache-first; FRED_API_KEY to refresh
C.timeseries(df, "build/figures/render/housing_starts", target="png")          # pptx
C.timeseries(df, "build/figures/figures_pdf/housing_starts", target="pdf", caption_mode="host")  # paper
```
Paper: `figures.latex_figure("housing_starts", "…/housing_starts.pdf")`. Slide:
`figures.pptx_caption("housing_starts")`. Regenerate everything with `make -C tools all`.

## Caching discipline

Pulls cache to `data/cache/{source}_{id}.csv` (committed) so rebuilds are deterministic and
run offline; `refresh=True` re-pulls. Keys via env vars (`FRED_API_KEY`, …) — never committed.

## Adding a series / chart type

Add a friendly name to `series_registry.yaml` (source + id + optional `yoy`). New chart type →
add a function to `chart_lib.py` reusing `_use_target`/`_finish` so it inherits style, target,
and caption handling. Add a `captions.yaml` entry for anything that gets a caption.

## Conventions (house-style.md, AER)

Booktabs tables (no vlines/shading, ≤9 cols, leading-zero decimals, SEs in parentheses not
stars, Panel A/B, source-note last); vector figures; math italic scalars, bold vectors, script
sets, blackboard only for ℝ/ℤ/ℕ. Tag grammar: `· In the data …` charts · `· <concept>`
diagrams · `· In the (macro-)news …` news.
