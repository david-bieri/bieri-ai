# Teaching Session Notes

**Last session:** 2026-06-18
**Topic:** Week 2 (Real Estate Economics) decks [L2.1–L2.3] · theory/empirics diagram+chart tooling · slide_lib refactor · migration to bieri-ai monorepo
**Horizon:** SU26 ends July 5 · final exam July 1–6 · V1–V4 + Week 2 not yet recorded

---

## Project configuration
**Prefix:** TEACHING
**Repo:** github.com/david-bieri/bieri-ai (monorepo — replaces bieri-claude/teaching/research/admin)
**Registry:** domains/teaching/SKILLS_MANIFEST.md
**Skill namespace:** `teaching-*` (hyphen) — was `course:*`. Skills are platform-agnostic `skill.md`, wrapped by `adapters/claude/wrap_skill.py` → `.skill`.
**Dispatch:**
  → bieri-ai repo     (skills/, domains/, tools/ — commit + push; this is now the source of truth)
  → Claude Customize  (.skill produced by the Claude adapter — Cowork → Customize → Skills → +)
  → OneDrive/Teaching/ (content only: PPTX decks, narration, KB working copies)
  → Canvas / Panopto   (student-facing video)
**Horizon:** SU26 ends July 5 · final exam July 1–6

> **Short code:** course is **SU26** (Summer 2026), never "SS26." `build_kb.py` VINTAGE_MAP already maps SU26→Summer 2026; deck footers read "Prof. Bieri – Summer 2026."

---

## 1. Completed this session

Week 2 Real Estate Economics — three async lecture videos, KB-grounded, house style, narration embedded; plus a refactor of the deck-build code into reusable libraries.

- ? `V1_SupplyDemand_L2-1.pptx` [L2.1] (13 slides, ~9.9 min) — S/D, movement vs. shift, build-lag; **Linkages discussion launch** (closing synthesis)
- ? `V2_MarketEquilibrium_L2-2.pptx` [L2.2] (14 slides, ~10.2 min) — clearing, price mechanism, comparative statics, disequilibrium/transaction zone
- ? `V3_Elasticity_L2-3.pptx` [L2.3] (16 slides, ~12.0 min) — PED/PES, determinants, supply fan; sets up Elasticity Analysis
- ? `Week2_Narration_Scripts.md` — combined scripts, 130 wpm, longest note 123 w (< 160)
- ? `slide_lib.js` — core builders factored out of build_week2.js; course-parameterized footer (setCourse())
- ? `diagram_lib.js` v1.0.0 — theory diagrams + empirics charts (registerDiagrams)
- ? `build_unit_TEMPLATE.js` — generalizable copy-to-start scaffold (wires both libs; one of each slide type)
- ? `build_week2.js` — slimmed to require both libs (verified byte-parity: 13/14/16 slides, fan render identical)
- ? `SKILLS_MANIFEST_additions.md` — paste-ready, corrected for the monorepo (teaching-* namespace, scripts/ paths)

News hooks (verified, current): NAR/Reuters homebuilding low (V1); HousingWire lock-in (V2); Dallas Fed Texas apartment glut (V3).

---

## 2. Pending dispatch

**[Target: bieri-ai repo — commit + push]**
```
# Bundle the libraries + template inside the compose-slides skill
skills/teaching-compose-slides/scripts/slide_lib.js
skills/teaching-compose-slides/scripts/diagram_lib.js
skills/teaching-compose-slides/examples/build_unit_TEMPLATE.js
# Update the skill's reference doc (diagram/chart families + tag convention)
skills/teaching-compose-slides/references/slide-library.md
# Domain state
domains/teaching/SKILLS_MANIFEST.md           # apply SKILLS_MANIFEST_additions.md
domains/teaching/TEACHING_SESSION_NOTES.md    # this file

git add skills/teaching-compose-slides domains/teaching
git commit -m "Week 2 econ decks; factor slide_lib + diagram_lib into compose-slides; theory/empirics tagging"
git push
```

**[Target: OneDrive/Teaching/Slides/SU26/]** (content, not infrastructure)
- The three Week 2 PPTX + `Week2_Narration_Scripts.md`
- `build_week2.js` — per-unit build source (work product; NOT in repo unless you adopt an examples/ convention for it)

**[Target: Claude Customize — after wrapping]**
- Run `python adapters/claude/wrap_skill.py skills/teaching-compose-slides`, then install the produced `.skill`
- Same for `teaching-build-kb` once v1.1.0 is built

**[Target: Canvas / Panopto — when recorded]**
- Record V1–V3 → virginiatech.hosted.panopto.com → embed in Week 2 module (📊)
- Caption review: "price elasticity," "comparative statics," "disequilibrium," "transaction zone"

**[Carried forward — confirm status]**
- V1–V4 Week 1 recordings → Panopto; spring answer-key/Blended Teaching audit (household calc −214 not −420)

---

## 3. Decisions made this session

**Migrated to the bieri-ai monorepo.** Single source of truth replacing the five separate repos. Skills are platform-agnostic `skill.md` under `skills/teaching-*`, wrapped by `adapters/` for Claude or Manus. Domain state (manifest, session notes) lives in `domains/teaching/`. Universal utilities only in root `tools/`.

**`.js` file homes settled:**
- `slide_lib.js` + `diagram_lib.js` → `skills/teaching-compose-slides/scripts/` (bundled skill resources; parallel to `teaching-build-kb/scripts/build_kb.py`). In the monorepo, the bundled copy is canonical — no separate Shared Scripts copy.
- `build_unit_TEMPLATE.js` → `skills/teaching-compose-slides/examples/` (new examples/ convention).
- `build_week2.js` → OneDrive content (per-unit work product), since the repo is infrastructure, not a content store.

**Refactor: builders factored into `slide_lib.js`.** build_week2.js previously carried ~150 lines of duplicated slide-builder boilerplate. Now the builders live once in `slide_lib.js`; per-unit scripts only write content. Verified behavior-preserving (parity render). Removes drift risk between units.

**Theory↔empirics is a tag convention** — `· <concept>` (theory diagram), `· In the data …` (empirics/stylized-fact chart), `· In the (macro-)news …` (news). A concept can run model → data → story (V3 does).

**[L2.3] collision resolved — no renumbering.** The old `[L2.3]` "Market Analysis" deck in the KB is a pre-renumbering artifact (now `[L1.3]`); the KB predates that fix. Week 2 Elasticity owns `[L2.3]`. Fix = rebuild the KB.

**Folded into teaching-compose-slides, not a new skill.** `teaching-diagrams` stays a low-priority candidate (split only if catalog > ~8 builders or a second course needs its own set).

**Manifest additions recorded** in `SKILLS_MANIFEST_additions.md` (not yet applied — see §2).

---

## 4. Latent issues surfaced

- **KB is stale** — still reflects pre-renumbering Week-1 tags (`[L2.3]`, `[L2.3e]`). Rebuild before generating assessments.
- **`teaching-compose-slides` skill.md** still references spring module numbering for `[L{mod}.{lec}]`; add the SU26 note when v1.2.0 is built.
- **Old manifest/notes references to `course:*` and the four-repo layout** are obsolete — anything still pointing there should be repointed to `bieri-ai` / `teaching-*`.
- **`chartSlide` question line** sits close to the footer on long questions; tighten if needed.

---

## 5. Open questions

- **Recording schedule** — V1–V4 (Week 1) + Week 2: when? Panopto pipeline unstarted.
- **`build_week2.js` placement** — leave in OneDrive (recommended), or adopt `skills/teaching-compose-slides/examples/` for per-unit build scripts too?
- **V1/V2 on-screen [L2.x]** — re-record title segment in Descript, or accept old codes on existing recordings?
- **VLLI Fall 2026 course** — status vs. sabbatical travel.

---

## 6. Suggested next session

**Before a new chat:** commit the skill bundling + domain state to bieri-ai; apply SKILLS_MANIFEST_additions.md; save decks + build_week2.js to OneDrive.

**Then open a new chat and say:**

> "Read TEACHING_SESSION_NOTES.md. Rebuild the course KB with teaching-build-kb so the stale [L2.3]/[L2.3e] Week-1 tags resolve to [L1.x], then build the Week 3 Real Estate Law decks [L3.x] · SU26. Start from skills/teaching-compose-slides/examples/build_unit_TEMPLATE.js; use teaching-news-hooks and teaching-video-scripts."

**Context for next session:**
- Week 3 emoji: ⚖️ · codes [L3.1]+ (SU26 Module 3 = Real Estate Law)
- teaching-compose-slides v1.2.0 + teaching-build-kb v1.1.0 are pending
- Build scaffold: `build_unit_TEMPLATE.js` — copy, rename build_week3.js, fill content
- `slide_lib.js` + `diagram_lib.js` are the bundled engine; reuse for any course (setCourse() for UAP 4714)
