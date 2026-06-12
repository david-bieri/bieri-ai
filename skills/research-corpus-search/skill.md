# research:corpus-search

Search a large PDF archive for every reference to a target term or named entity:
extract text in parallel with PyMuPDF, filter out look-alike false positives,
and emit both a machine-readable CSV and a human-readable report — while
isolating the scanned/unreadable PDFs that need an OCR pass first.

---

## When to invoke

Trigger on: "search the archive for X", "find every mention of <person/term>
across these PDFs", "hunt the corpus for references to ...", "which documents
cite <entity>", "build a citation/mention index over this PDF collection", or
any request to scan a folder of PDFs for occurrences of a term and tabulate the
hits.

Also invoke when a corpus search returns suspiciously few hits and the cause may
be **untexted PDFs** (scanned images with no text layer) — that is the signal to
branch into the OCR fallback (see *Handling unreadable PDFs*).

Worked example throughout: searching a ~12,000-PDF archive for references to
Justice **Felix Frankfurter**, disambiguated from the newspaper *Frankfurter
Allgemeine Zeitung*.

---

## Inputs and outputs

**Inputs**
- A root folder of PDFs (searched recursively).
- One or more **search terms** (the entity/phrase to find).
- Zero or more **exclusion terms** — phrases that, when co-located with a hit,
  mark it as a false positive (disambiguation).

**Outputs** (all written under one output folder, auto-created if missing)
- `matches.csv` — one row per hit: file, page, matched term, surrounding snippet.
- `report.txt` — grouped, human-readable summary (per file, with page + context).
- `unreadable.txt` — the PDFs that yielded no extractable text (OCR candidates).

---

## Workflow

### Step 1 — Point at the corpus and define the target
Confirm the PDF root. Define the positive search term(s) and any exclusion
term(s). For named people, names that collide with institutions or place names
**always** need exclusions (see *Disambiguation*).

### Step 2 — Run the parallel search
Use the bundled `scripts/search_corpus.py`. It walks the archive recursively,
opens each PDF with PyMuPDF (`fitz`), and searches page text. Key behaviours
worth preserving in any reimplementation:

- **Parallelism.** PDFs are independent; process them across worker processes
  (`ProcessPoolExecutor`) so a 12k-file archive completes in minutes, not hours.
- **Quiet output.** PyMuPDF emits noisy internal warnings on malformed PDFs.
  Suppress them per worker with `fitz.TOOLS.mupdf_display_errors(False)` so the
  progress bar and report stay clean.
- **Progress.** Wrap the file loop in `tqdm` — over thousands of files you want
  a live count and ETA.
- **Auto-create the output directory** before writing, so the run never dies at
  the last step on a missing folder.

### Step 3 — Capture the unreadable files
A file that opens but exposes **no text on any page** is almost certainly a
scanned image with no OCR layer. Do **not** count it as "zero mentions" — record
it to `unreadable.txt`. In a typical archival collection this set is large
(≈4,000 of 12,000 in the Frankfurter corpus).

### Step 4 — Hand off to the OCR pass (if needed)
Run the OCR fallback (`ocrmypdf` + Tesseract) over `unreadable.txt` into a
parallel output folder, then re-run Step 2 against the OCR'd copies and merge the
new hits. This second pass is a sibling workflow; see *Handling unreadable PDFs*.

### Step 5 — Review and interpret
Read `report.txt` for context around each hit; use `matches.csv` for downstream
analysis (counts per document, timeline, etc.). Spot-check a sample of snippets
to confirm the disambiguation held.

---

## Disambiguation

A bare surname match is rarely what you want. Searching for **Frankfurter**
returns both the Justice and the German newspaper *Frankfurter Allgemeine
Zeitung* (and "frankfurter" the sausage). Two complementary tactics:

- **Require the full/qualified form** as the positive term where possible
  (`"Felix Frankfurter"`, `"Justice Frankfurter"`) rather than the bare surname.
- **Exclude co-located look-alikes** — flag a hit as a false positive when the
  surrounding window also contains an exclusion phrase
  (`"Allgemeine Zeitung"`, `"FAZ"`). The bundled script supports both: positive
  `--term` (repeatable) and `--exclude` (repeatable), with a configurable
  context window.

Record the exclusion list you used in the run notes — it is part of the result's
provenance.

---

## Handling unreadable PDFs

Scanned PDFs with no text layer are invisible to text search. The pattern:

1. Search pass writes `unreadable.txt` (the no-text files).
2. OCR pass: `ocrmypdf` (Tesseract backend) converts each into a searchable copy
   in a **parallel output folder** — never overwrite the originals. Add the
   relevant language packs up front (e.g. Tesseract's `deu.traineddata` for
   German-language documents).
3. Re-run the search against the OCR'd folder; merge new hits into the report.

When this OCR pass is itself captured as a skill, this skill's `depends_on`
should gain `research:ocr-batch`.

---

## Reference implementation

`scripts/search_corpus.py` is a self-contained, runnable reconstruction of the
search pass (PyMuPDF + parallel workers + disambiguation + CSV/report/unreadable
outputs). It generalises the original `search_frankfurter.py`. Reconcile it
against your working copy before treating it as canonical.

```
python scripts/search_corpus.py \
  --archive "/path/to/pdf_archive" \
  --out     "./frankfurter_out" \
  --term "Felix Frankfurter" --term "Justice Frankfurter" \
  --exclude "Allgemeine Zeitung" --exclude "FAZ" \
  --workers 8 --context 200
```

Requires: `pip install pymupdf tqdm`.

---

## QA checklist

- [ ] Output folder auto-created; `matches.csv`, `report.txt`, `unreadable.txt`
      all written.
- [ ] PyMuPDF internal warnings suppressed — console shows only the progress bar.
- [ ] Disambiguation applied: a sample of hits is the *intended* entity, not the
      look-alike.
- [ ] `unreadable.txt` reviewed; OCR pass run if its count is non-trivial.
- [ ] Exclusion terms recorded in the run notes for provenance.
