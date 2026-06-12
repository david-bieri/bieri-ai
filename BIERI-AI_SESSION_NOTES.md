# BIERI-AI Session Notes

**Last session:** 2026-06-12
**Topic:** Opened the `research:` domain — created `research:corpus-search` v1.0.0 (first research skill), audited green, pushed (CI passed), wrapped + deployed to Claude Customize. Logged two research candidates with triggers.
**Horizon:** No hard deadline. Next goal = first live corpus-search run, then the OCR pass.

---
## Project configuration
**Prefix:** BIERI-AI
**Registry:** `domains/*/SKILLS_MANIFEST.md` · `CONTRIBUTING.md` + `AGENTS.md` (contract) · `architecture/BIERI_AI.md`
**Dispatch:**
  → git push            (`david-bieri/bieri-ai`, branch `main`)
  → Claude Customize    (re-wrapped `.skill` files — Cowork → Customize → Skills → + → upload)
  → Manus               (`dist/manus/<skill>/SKILL.md` directories)
**Horizon:** none fixed; next is the first live corpus-search run
---

## 1. Completed this session

- ✓ **`research:corpus-search` v1.0.0** — `skills/research-corpus-search/`: `skill.md` (colon H1, no frontmatter), `metadata.yaml` (desc 199 chars, no `name`, `depends_on: []`), and bundled `scripts/search_corpus.py` (parallel PyMuPDF + disambiguation + CSV/report/unreadable outputs, generalised from `search_frankfurter.py`). First skill in the `research:` namespace.
- ✓ Auditor: single-skill PASS; `audit_skill.py --all` → **Library result: PASS (25/25**, zero FAIL/WARN).
- ✓ `origin/main` @ **fa697d1** (pushed). CI `skill-contract-audit` **#2 green** (9s) — confirms compliance at the shared choke point, not just locally.
- ✓ Wrapped + **deployed** the new skill to Claude Customize (`dist/claude/research-corpus-search.skill` uploaded).
- ✓ `domains/research/SKILLS_MANIFEST.md`: registered `research:corpus-search`; logged candidates `research:ocr-batch` and `research:codespaces-bootstrap` with concrete trigger conditions; noted the three form one archive-research pipeline.

## 2. Pending dispatch

**Manus** — re-wrap/deploy `research:corpus-search` (`python adapters/manus/wrap_skill.py --all -o dist/manus`) if Manus is still in active use. (See open question on Manus.)

**GitHub** — enable branch protection on `main` requiring the `skill-contract-audit` check (decision below). Turns the CI flag into a hard merge gate. Use admin bypass to preserve direct-push / bundle delivery.

**Project knowledge** — re-upload this refreshed `BIERI-AI_SESSION_NOTES.md` (the copy in Project knowledge was the stale `f2d3e7c` version, predating the CI/AGENTS.md drift-guard work).

## 3. Decisions made this session

- **Research harvest = three separate skills, not a combined toolkit.** Order: `corpus-search` (done) → `ocr-batch` → `codespaces-bootstrap`. Rationale: one repeatable workflow per skill; distinct triggers, dependencies, and tooling (`fitz`+`tqdm` vs `ocrmypdf`+Tesseract vs devcontainer/dotfiles); the pipeline is expressed through the `depends_on` graph, not by merging files.
- **`corpus-search` bundles a reference script** (`search_corpus.py`), a reconstruction of `search_frankfurter.py` from the documented design — **reconcile against the working copy** before treating it as canonical.
- **Build `ocr-batch` against real data, not in the abstract** — its trigger is acting on an actual `unreadable.txt`, which only exists after a live corpus-search run.

## 4. Latent issues surfaced

- **Divergent auditor copy.** `adapters/claude/audit_skill.py` is the **old `course:`-era auditor** (checks `SKILL.md` frontmatter, warns on `course:` deps) — it contradicts the live contract. The canonical, contract-aligned auditor is `skills/teaching-skill-builder/scripts/audit_skill.py` (what `AGENTS.md` and CI invoke). **Delete or re-export** the adapters copy; it's a footgun for any session that runs it by mistake.
- **Branch protection not yet enabled.** CI flags non-compliant pushes (red check + email) but doesn't *block* direct pushes to `main` until protection requires the check. Decided to enable (see §2/§3).
- **`search_corpus.py` is a reconstruction**, not the live `search_frankfurter.py`. Reconcile.
- **Seven freeform webdev skills** still use the "This skill defines…" prose style rather than the fuller skill-builder template. Pass audit; deeper restructure is optional polish.

## 5. Open questions

- Run `research:corpus-search` on the full ~12k archive **now**, or build `ocr-batch` first? (Recommendation: run first — it produces the `unreadable.txt` that is the trigger for `ocr-batch`.)
- Is **Manus** still an active deployment target, or is delivery now Claude-Customize-only? (Affects whether the Manus re-wrap in §2 is needed.)
- Enable branch protection on `main` this session, or defer?

## 6. Suggested next session

> "Read `BIERI-AI_SESSION_NOTES.md`, then do a live `research:corpus-search` run on the ~12k Frankfurter archive — terms `Felix Frankfurter` / `Justice Frankfurter`, exclude `Allgemeine Zeitung` / `FAZ`. Review `report.txt` and `unreadable.txt`; if the unreadable set is non-trivial (~4k expected), that is the trigger to build `research:ocr-batch` against it. Then enable branch protection on `main` if not already done, and delete the stale `adapters/claude/audit_skill.py`."
