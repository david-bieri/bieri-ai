# Teaching Session Notes

**Last session:** 2026-06-19
**Topic:** Figure system — teaching-diagrams + teaching-charts (TikZ + Python), Palatino/AER house standard, build-kb v1.1.0, compose-slides v1.2.0 embed path, user guide
**Horizon:** SU26 ends July 5 · final exam July 1–6 · V1–V4 + Week 2 not yet recorded

---

## Project configuration
**Repo:** github.com/david-bieri/bieri-ai (monorepo) · namespace `teaching-*`
**Registry:** domains/teaching/SKILLS_MANIFEST.md
**Dispatch:** bieri-ai repo (skills/, domains/, tools/ — commit+push) · Claude Customize (.skill via adapters/claude/wrap_skill.py) · OneDrive/Teaching (content) · Canvas/Panopto (student-facing)
**Horizon:** SU26 ends July 5 · final exam July 1–6
> Short code: **SU26** (Summer 2026), never "SS26."

---

## 1. Completed this session

Built the figure system as two new skills + folded AER/Palatino standards + implemented two pending code upgrades.

- ? `teaching-diagrams` v1.0.0 — TikZ theory diagrams. `bieri-tikz.sty` (Palatino/Heros, palette, named styles), `_standalone.tex`, 6 templates (supply_fan, sd_cross, shift, elasticity_slopes, market_cycle, system_triangle) + process_overview. All compile to cropped PDF; `\input`-able in Beamer.
- ? `teaching-charts` v1.0.0 — empirical charts + shared caption/standards layer. `chart_lib.py` (line/bar/scatter-dot/box; target png/pdf/pgf; caption off/host/baked; font auto-register), `datasources.py` + `series_registry.yaml` (FRED/BEA/Census/BLS, cache-first), `figures.py` (pptx_caption, latex_figure, latex_table, dump_json), `captions.yaml`, `bieri.mplstyle`, `bieri-preamble.tex`, `house-style.md`, `build_charts.py`.
- ? `teaching-build-kb` **v1.1.0** — `extract_assets()` detects pictures/tables/charts; image-only slides no longer dropped; emits [FIGURE]/[TABLE]/[CHART], renders tables as markdown. Tested on synthetic deck.
- ? `teaching-compose-slides` **v1.2.0 embed path** — `figureSlide()` + `loadCaptions()` in slide_lib.js embed a figure PNG and pull caption from captions.json (via figures.dump_json). Tested.
- ? `tools/Makefile` — one-command rebuild (diagrams + charts + captions.json). Verified.
- ? `USER_GUIDE.md` + `process_overview.png` — manual with dogfooded flow diagram.
- ? `SKILLS_MANIFEST_additions.md` — paste-ready (promotes both skills to Active; logs build-kb/compose-slides; records decisions).
- ? Pre-commit fixes: both new skill descriptions trimmed to ≤200 chars (audit limit — were 224/227, now 181/184); `tools/Makefile` made monorepo-aware (`REPO`/`DIAGRAMS`/`CHARTS` overridable paths, outputs to `build/figures/`) and **verified building from `tools/`** in a mock repo tree (8 PDFs + previews + chart + captions.json).

Proven dual-target: `beamer_demo.tex` compiles with diagram `\input` + chart `\includegraphics` + caption; pptx via figureSlide.

---

## 2. Commit checklist (self-contained)

**A · Pre-commit, local (once):**
- Install TeX packages: `texlive-fonts-extra` (newpx/XCharter), `texlive-plain-generic` (binhex for newtxmath), `tex-gyre` (Heros/Pagella).
- (Optional) run the repo skill audit on the two new skills; descriptions are already ≤200.

**B · Commit to bieri-ai** — files (see PowerShell block this session):
```
skills/teaching-diagrams/{skill.md, scripts/{bieri-tikz.sty,_standalone.tex}, templates/*.tikz, references/house-style.md}
skills/teaching-charts/{skill.md, scripts/*, references/{house-style.md, USER_GUIDE.md, process_overview.png}}
skills/teaching-compose-slides/scripts/slide_lib.js     # v1.2.0 figureSlide/loadCaptions (file only)
skills/teaching-build-kb/scripts/build_kb.py            # v1.1.0 asset detection (file only)
tools/Makefile
domains/teaching/TEACHING_SESSION_NOTES.md
git add skills tools domains/teaching && git commit -m "..." && git push
```

**C · Apply manually (not a file copy):**
- Paste the four blocks from `SKILLS_MANIFEST_additions.md` into `domains/teaching/SKILLS_MANIFEST.md`.

**D · Post-commit verification (first real use — known caveats):**
1. **Live data:** run ONE pull per source (FRED/BEA/Census/BLS) with keys set — the four adapters are **cache-tested only**; the live `_http_get` paths (esp. BEA NIPA parse, BLS POST) are unverified.
2. **Fonts:** compile one diagram locally to confirm `newpx`/`tex-gyre`/`binhex` are present (step A).
3. **Caption seam:** `figureSlide` looks for `captions.json` next to `slide_lib.js`, but `make` writes it to `build/figures/`. Decide the wiring — pass `loadCaptions("…/build/figures/captions.json")` or copy the file into the compose-slides scripts dir.
- (sankey needs `pip install plotly kaleido`; not bundled.)

**Carried forward:** V1–V4 + Week 2 recordings → Panopto; spring answer-key audit (−214).

**Claude Customize:** wrap + install teaching-diagrams, teaching-charts; re-wrap teaching-build-kb, teaching-compose-slides.

---

## 3. Decisions made this session

- **Type → Palatino + Helvetica.** Body+math = Palatino (`newpxtext`/`newpxmath`); headers = Heros (`\sfdefault=qhv`; Arial in Office). Chosen over XCharter (elegance) and Garamond (Garamond math too weak). Figures must use the body's math companion. `tgheros.sty` clashes with newpx → set `\sfdefault` directly.
- **Standard → AER** (over JPE/Chicago): booktabs tables (no vlines/shading, ≤9 cols, leading-zero decimals, SEs in parens not stars, Panel A/B, source last), vector figures, AER math conventions, Chicago author-date. Encoded in house-style.md / bieri-preamble.tex / latex_table / chart_lib.
- **Engines split:** theory→TikZ, empirics→Python (sankey=plotly optional). Mirrors the theory/empirics tag convention.
- **Skills split confirmed:** teaching-diagrams + teaching-charts separate from compose-slides; native pptxgenjs diagram_lib/chartSlide remain the quick-draft tier in compose-slides.
- **Shared layer** (figures.py, captions.yaml, house-style.md, bieri-preamble.tex) lives in **teaching-charts**; house-style.md duplicated into teaching-diagrams/references (sync via meta:consistency-check).
- **Makefile → `tools/`** in the monorepo.
- **Caption toggle** off/host/baked; captions authored once in captions.yaml, bridged to JS via captions.json.

---

## 4. Latent issues
- KB still stale (pre-renumbering [L2.3]/[L2.3e]); rebuild with v1.1.0 before generating assessments.
- Data APIs cache-tested only (no sandbox egress) — verify live params per source on first pull.
- house-style.md duplicated across two skills — meta:consistency-check (candidate) should keep them in sync.
- sankey needs plotly+kaleido (not bundled).

---

## 5. Open questions
- Recording schedule (V1–V4 + Week 2) — Panopto pipeline unstarted.
- Promote diagram_lib.js (native quick-draft) usage vs always TikZ? (TikZ now canonical for publication.)
- VLLI Fall 2026 course status vs sabbatical.

---

## 6. Suggested next session
**Before a new chat:** commit skills + tools/ + domains to bieri-ai; apply SKILLS_MANIFEST_additions.md; install TeX font packages locally.

**Then say:**
> "Read TEACHING_SESSION_NOTES.md. Rebuild the KB with teaching-build-kb v1.1.0 (resolves stale [L2.3]/[L2.3e] → [L1.x] and now captures figures/tables), then build Week 3 Real Estate Law decks [L3.x] · SU26 from examples/build_unit_TEMPLATE.js, using teaching-diagrams + teaching-charts for figures."

**Context:** Week 3 emoji ⚖️ · codes [L3.1]+ · `make` rebuilds all figures · `from_registry()` for data charts · `figureSlide()` to embed.
