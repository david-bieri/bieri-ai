# teaching:diagrams

## When to invoke

Trigger on: "make a diagram"; "supply/demand diagram"; "shift" or "elasticity" diagram;
"supply fan"; "market cycle"; "system triangle"; "TikZ figure"; any theory diagram (no
real data) for a slide, Beamer talk, or paper. Always use the bundled `bieri-tikz.sty`
plus a template in `assets/` — never hand-roll TikZ from memory.

---

TikZ theory diagrams in Bieri house style (Palatino body+math, Heros headers). Dual-target:
cropped PDF for pptx embed, or `\input` natively into Beamer/LaTeX. For empirical charts
from data, use `teaching:charts`.

---

## Bundled resources

- `scripts/bieri-tikz.sty` — single source of visual truth: Palatino (`newpxtext`/`newpxmath`)
  body+math, Heros sans (`\sfdefault=qhv`), the palette (`bieriRed`/`bieriDark`/`bieriGray`),
  named styles (`bieri demand`/`supply`/`curve2`/`curve3`/`guide`/`eqdot`/`clabel`/`note`), and
  `\bieriaxes{w}{h}`. Pass `[nofont]` when the host (Beamer theme) sets fonts.
- `scripts/_standalone.tex` — wrapper that compiles one `.tikz` body to a cropped PDF.
- `assets/*.tikz` — body-only templates: `supply_fan`, `sd_cross`, `shift`,
  `elasticity_slopes`, `market_cycle`, `system_triangle` (+ `process_overview`).
- `references/house-style.md` — AER figure/type standard (canonical copy in `teaching:charts`; synced).

## Workflow

**pptx** — compile the body to a cropped vector PDF, then embed (via `teaching:compose-slides`
`figureSlide`, which uses the PNG preview):
```
pdflatex "\def\bieribody{assets/sd_cross.tikz}\input{_standalone.tex}"
```
or `make -C tools all` (regenerates every figure to `build/figures/`).

**Beamer/LaTeX** — load once, then `\input` the body (true vector, fonts match the doc):
```latex
\usepackage[nofont]{bieri-tikz}     % host preamble sets Palatino/Heros
\begin{frame}{The supply fan}\input{assets/supply_fan.tikz}\end{frame}
```
For a captioned figure in a paper, wrap with `teaching:charts` `figures.latex_figure`.

## Adding a diagram

Copy the nearest `assets/*.tikz`, keep only `\begin{tikzpicture}…\end{tikzpicture}`, use
`\bieriaxes` and the named styles (never hard-code colors/line widths), label curves with
`bieri clabel`. Add a caption entry in `teaching:charts` `captions.yaml`. Keep diagrams
caption-free; the slide or `\caption` carries the text.

## Conventions (house-style.md, AER)

Palatino body+math, Heros headers; variables italic, vectors bold; vector PDF output;
schematic — no axis numbers unless pedagogically required.
