# Loading Skills into Claude

How to take the `teaching-*` skills from the `bieri-ai` repo to live, toggleable
skills in Claude. Two stages: **wrap** (adapter → Claude package) and **load** (upload).
Lives at `domains/teaching/`.

> Sources for the load steps: Claude Help Center, "Use skills in Claude"
> (support.claude.com) and Agent Skills overview (docs.claude.com), verified 2026-06.

---

## 1 · Wrap each skill into a `.skill` package

`adapters/claude/wrap_skill.py` reads `skill.md` + `metadata.yaml`, derives the colon
name from the directory (`teaching-diagrams` → `teaching:diagrams`), generates the
`SKILL.md` frontmatter, and zips `SKILL.md` + `scripts/`/`references/`/`assets/`.

```powershell
cd "C:\Users\bieri\OneDrive - Virginia Tech\Documents\GitHub\bieri-ai"

# sanity check — names/descriptions/versions resolve, no errors
python adapters\claude\wrap_skill.py --all --dry-run

# wrap everything under skills/ into dist\claude\*.skill
python adapters\claude\wrap_skill.py --all -o dist\claude

# wrap just one:
# python adapters\claude\wrap_skill.py skills\teaching-diagrams -o dist\claude
```

A `.skill` file is a ZIP with a different extension. Claude's uploader asks for a ZIP,
so copy them to `.zip` first:

```powershell
Get-ChildItem dist\claude\*.skill | ForEach-Object {
  Copy-Item $_.FullName ($_.FullName -replace '\.skill$','.zip')
}
```

## 2 · Enable Skills (one-time prerequisite)

Custom Skills run in Claude's code-execution environment, so it must be enabled, on a
Pro / Max / Team / Enterprise plan. Team/Enterprise: an owner enables "Code execution and
file creation" + "Skills" in Organization settings. Max/Pro: enable under Customize → Skills.

## 3 · Upload each skill

In claude.ai or Cowork: **Customize → Skills → "+" → "+ Create skill" → upload the ZIP**
(a ZIP containing the skill folder). It appears in your skills list; **toggle it on**.
One ZIP per skill. Uploaded skills are private to your account; Team/Enterprise can share
with colleagues or org-wide.

Upload the full set together (they reference each other):
`teaching-charts` (shared caption layer), `teaching-diagrams`, `teaching-compose-slides`,
`teaching-build-kb` — plus `teaching-news-hooks`, `teaching-video-scripts`,
`teaching-assess-from-kb`, `session-handover` as needed.

## 4 · Verify

Skills activate by description, on-demand. In a fresh session, give a triggering prompt
("make a supply-and-demand diagram in house style"; "rebuild the course KB") and confirm
the skill engages. If one won't fire, broaden the `description` in its `metadata.yaml`,
re-wrap, re-upload.

---

## Gotchas

- **No cross-surface sync.** A skill uploaded to claude.ai is not available via the API or
  Claude Code, and vice-versa — upload separately per surface.
- **Claude Code = filesystem, no upload.** Point it at `.claude/skills/<name>/SKILL.md`.
  Unzip a `.skill` into `.claude/skills/`, or wire the repo's wrapped output in.
- **Re-uploading = updating.** Bump the skill (`metadata.yaml` version + `updated`), re-wrap,
  upload the new ZIP; delete the old entry first if it doesn't overwrite cleanly.
- **The build toolchain is the real dependency.** These skills invoke `pdflatex`, `make`,
  Node/pptxgenjs, python. Drive build-heavy work in a Cowork/Code session that provides
  them (one-time: `texlive-fonts-extra`, `texlive-plain-generic`, `tex-gyre`); the uploaded
  skills supply the how.
- **`depends_on` is documentation, not an installer.** `teaching-diagrams` depends on
  `teaching:charts` (shared caption layer) — make sure charts is uploaded too.

## Quick reference

| | Wrap | Load |
|---|------|------|
| **claude.ai / Cowork** | `wrap_skill.py --all -o dist\claude`, copy `.skill`→`.zip` | Customize → Skills → "+" → Create skill → upload ZIP → toggle on |
| **Claude Code** | (none) | place skill dirs at `.claude/skills/<name>/SKILL.md` |
| **API** | (none) | upload via the Skills API (`/v1/skills`) |
