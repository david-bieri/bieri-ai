# Research Skills Manifest — Prof. David Bieri

Skill registry for David Bieri's research workflows (`research:*` namespace).

---

## Installed Skills

| Skill | Version | Status | Updated |
|-------|---------|--------|---------|
| `research:corpus-search` | 1.0.0 | Active | 2026-06-12 |

### `research:corpus-search`
Search a large PDF archive for a target term or entity via parallel PyMuPDF
extraction, with disambiguation (positive + exclusion terms), CSV/report output,
and an OCR fallback for scanned PDFs. Worked example: the ~12k-PDF Felix
Frankfurter corpus, disambiguated from *Frankfurter Allgemeine Zeitung*.
Bundles `scripts/search_corpus.py`. `depends_on: []` today; gains
`research:ocr-batch` once the OCR pass is captured.

---

## Candidate skills

| Skill | What it does | Build when |
|-------|--------------|------------|
| `research:ocr-batch` | Batch-OCR scanned/untexted PDFs (`ocrmypdf` + Tesseract, German pack) into a parallel folder, then feed `research:corpus-search` for a re-search pass. | Build when running the ~4,000 unreadable Frankfurter PDFs through OCR — i.e. the next time an `unreadable.txt` from a corpus search is acted on. |
| `research:codespaces-bootstrap` | Stand up a reproducible browser-based dev environment (GitHub Codespaces + `devcontainer.json` + `dotfiles`) so research tooling runs identically on home, office, and laptop despite institutional admin-rights limits. | Build when the Codespaces/devcontainer setup is first done end-to-end and worth replaying — captures the bootstrap so it isn't re-derived per machine. |

Notes on clustering: these three form one **archive-research pipeline** —
`corpus-search` (read) <- `ocr-batch` (repair) <- `codespaces-bootstrap`
(environment). They are kept as separate skills (one workflow each) rather than a
single combined toolkit; see the harvest-scope decision in the session notes.

---

## Update Log

| Date | Change |
|------|--------|
| 2026-06-12 | Created `research:corpus-search` v1.0.0 (first `research:` skill). Logged `research:ocr-batch` and `research:codespaces-bootstrap` as candidates with trigger conditions. |
