
# course:build-kb

## When to invoke

Trigger on: "build the KB"; "update the knowledge base"; "run build_kb.py";
"add this semester's slides"; "KB is out of date"; "extract slides to markdown";
any mention of build_kb.py or the REALUAP2004_KB.md file.
Always use this skill — do not guess at script flags or filename patterns.

---

Guides the full workflow for extracting course slide content into a structured
Markdown knowledge base and uploading it to a Claude Project.

---

## Script location and invocation

The script lives wherever the user has saved it — typically in the Teaching folder
alongside the slide decks. Reference copy also bundled with this skill in `scripts/build_kb.py`.

### Standard invocation (Windows PowerShell)

```powershell
# Single semester
python build_kb.py "C:\Users\bieri\OneDrive - Virginia Tech\Teaching\UAP_2004" `
  REALUAP2004_KB.md --pattern "*_S26.pptx"

# Multiple semesters in one KB (most common)
python build_kb.py "C:\...\UAP_2004" REALUAP2004_KB.md `
  --pattern "*_S26.pptx,*_SU26.pptx,*_S24.pptx,*_S23.pptx"

# Slides split across folders
python build_kb.py "C:\...\Spring2026" REALUAP2004_KB.md `
  --also "C:\...\Spring2024"

# Omit speaker notes (halves file size)
python build_kb.py "..." REALUAP2004_KB.md --pattern "..." --no-notes
```

### Dependency

```powershell
pip install python-pptx
```

---

## Filename conventions

| Suffix | Semester | VINTAGE_MAP label |
|--------|----------|-------------------|
| `_S26` | Spring 2026 | "Spring 2026" |
| `_SU26` | Summer 2026 | "Summer 2026" |
| `_S24` | Spring 2024 | "Spring 2024" |
| `_S23` | Spring 2023 | "Spring 2023" |

**Critical:** The 2024 files are `*_S24.pptx` (with the S prefix), not `*_24.pptx`.
Always confirm the suffix with the user before constructing the `--pattern` argument.

---

## Module numbering — known divergence

The two main course iterations use the **same lecture numbers but different content**:

| Module | Spring 2026 | Spring 2024 |
|--------|-------------|-------------|
| 2 | Real Estate Value Drivers | RE Markets & Institutions I |
| 3 | Real Estate Economics | RE Markets & Institutions II |
| 5 | Time Value of Money | Community Planning & Financing |
| 10 | REITs | Urban Spatial Structure |
| 12 | Real Estate Development | RE Finance — Risk & Return |

The script handles this via vintage-aware `_MOD_S26` / `_MOD_S24` tables. When both
vintages appear in the same module, the heading shows both names:
`[Sp24] RE Markets & Institutions I  |  [Sp26] Real Estate Value Drivers`

---

## Common errors and fixes

### `AttributeError: 'NoneType' object has no attribute 'text'`
**Cause:** Some older PPTX files store notes panes as `None` rather than an empty frame.
**Fix:** Already handled in the current script via try/except around notes extraction.
If this error appears, the user has an older version of the script — replace with the
bundled copy.

### `No files matching pattern`
**Cause:** Wrong suffix or wrong folder path.
**Fix:** Run a quick count first:
```powershell
(Get-ChildItem -Recurse -Filter "*_S26.pptx" "C:\...\UAP_2004").Count
```
If zero, check for subfolders — slides may be nested one level deeper.

### Module labels look wrong for S24 content
**Cause:** The `_S24_VINTAGES` set controls which module table is used. If a vintage
string isn't in that set, it defaults to the S26 table.
**Fix:** Check `VINTAGE_MAP` dict — the detected vintage label must match exactly
what's in `_S24_VINTAGES = {"Spring 2024", "Spring 2023", "2024", "2023"}`.

### Duplicate files in manifest
**Cause:** OneDrive sync sometimes creates duplicate files.
**Fix:** The script deduplicates by resolved path. Warn the user to delete the extra
copy from their folder to keep the corpus clean.

---

## Output quality checks

After the run, verify:

1. **Deck count** matches expectation (e.g., 75 for S26+S24 combined)
2. **Module numbering note** appears in the KB header (confirms cross-vintage run)
3. **Vintage counts** in the "Included Course Iterations" section look right
4. **Tag distribution** — a healthy KB has roughly:
   - `[NEWS]`: 3–5 per deck (more in current semesters)
   - `[EXAMPLE]`: 2–4 per deck (heavier in finance/TVM modules)
   - `[LO]`: 1–2 per deck (title + recap)
5. **File size** — with notes: ~1.5 MB for 75 decks. Flag if >4 MB (approaching 5 MB Project limit).

---

## Upload to Claude Project

1. Open claude.ai → navigate to the Project
2. **Project knowledge** panel (left sidebar) → **+ Add content** → **Upload file**
3. Select the generated `.md` file
4. Confirm upload — the KB will be indexed and searchable within seconds

**After upload:** test with `project_knowledge_search` for a concept that should appear
(e.g., "economic base multiplier" or "bundle of rights"). If no results, check that the
file was added to the correct Project.

---

## Updating an existing KB

When new slides are added (new semester, revised decks):

1. Re-run with the full `--pattern` including all vintages
2. The script overwrites the output file — the old KB is replaced
3. In Claude Project: delete the old KB file, upload the new one
4. The KB does not support incremental updates — always regenerate from all sources

---

## Course-specific notes (REAL/UAP 2004)

- `review_S26.pptx` has no module prefix → lands in **Module 0 (General)**; correct behaviour
- S24 decks contain `FA, chapter N` cross-references (Floyd & Allen textbook); these
  are harmless in the KB and useful for S24 content searches
- The `2.1-Value_S26.pptx` source deck was distributed as a **PDF**, not PPTX — its
  content won't appear unless a PPTX version exists. The Summer 2026 video decks
  (V1–V4) cover this content programmatically.
