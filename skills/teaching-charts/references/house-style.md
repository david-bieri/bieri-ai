# House style — figures, tables, math (AER conventions)

Adopted standard: **AEA / *American Economic Review* style guide**
(https://www.aeaweb.org/journals/aer/style-guide). Chosen over JPE/Chicago because it
is a single, prescriptive, self-contained spec whose figure/table rules already match
this tooling. Citations follow Chicago author-date (AER ships `aea.bst`); the typeface
below is a house choice (journals re-typeset), not mandated by AER.

## Type
- **Body / math:** Palatino — `newpxtext` + `newpxmath` (LaTeX); "Palatino Linotype" (Office);
  "TeX Gyre Pagella" (matplotlib/Linux). Body and math are one family.
- **Headers / titles:** Helvetica — TeX Gyre Heros (`\sfdefault=qhv` in LaTeX); Arial (Office).
- Figures must use the body's math companion so labels match the running equations.

## Figures (AER)
- **Vector only** — vector PDF (or EPS). This tooling outputs cropped PDF; embed via
  `\includegraphics` (LaTeX/Beamer) or `addImage` (pptx). Raster images at ≥300 dpi.
- Variables in figures are *italic*; vectors/matrices **boldface** — same as the text.
- **Source note placed last**, after any other figure notes.
- Caption via `captions.yaml` → `figures.latex_figure()` (real `\caption`+`\label`); on a
  slide the deck carries the text (`caption_mode="off"`).

## Tables (AER)
- **Horizontal rules only; no vertical rules, no shading** (booktabs `\toprule/\midrule/\bottomrule`).
- **≤ 9 columns** including row headings (`latex_table` warns past this).
- Number tables with Arabic numerals; sections within a table are **Panel A, Panel B, …**.
- **Leading zero on all decimals**: `0.357`, never `.357` (`latex_table` enforces via `fmt`).
- **Report standard errors in parentheses — never significance stars/asterisks.**
- Column headings spelled out (no abbreviations); per-entry footnotes use lowercase
  letters (a, b, c). Source note placed last; full source cited in references.

## Math (AER)
- Scalars *italic* (default); vectors/matrices **boldface**; sets in script (`\mathcal`).
- **Blackboard bold ONLY for number systems** — $\mathbb{R},\mathbb{Z},\mathbb{N}$.
- Display equations on their own line, numbered consecutively at the **left margin**, Arabic
  in parentheses; appendix equations as (A1), (A2), …
- **At most two levels** of sub/superscripts.
- In-text fractions use a solidus with parenthesized numerator/denominator,
  e.g. $(a+b)/(c+d)$; display anything more complex.
- Preamble macros in `bieri-preamble.tex` encode these defaults.

## Headings (AER)
- Outline format: `I., II., …` for sections; `A., B., …` for subsections.
  The introduction gets **no** heading.

## Decimals & numbers (house default, AER-aligned)
- Leading zero on |x|<1; consistent decimal places within a column; thousands separators
  in text tables only where they aid reading.
