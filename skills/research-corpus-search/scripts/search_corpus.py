#!/usr/bin/env python3
"""
search_corpus.py — parallel PDF corpus search with disambiguation
=================================================================
A self-contained, runnable reconstruction of the Frankfurter corpus-search
workflow (generalises the original `search_frankfurter.py`). Walks a PDF
archive recursively, searches each file's text for one or more target terms,
filters out look-alike false positives, and writes:

    <out>/matches.csv      one row per hit (file, page, term, snippet)
    <out>/report.txt       grouped human-readable summary
    <out>/unreadable.txt   PDFs with no extractable text (OCR candidates)

Requires: pip install pymupdf tqdm

Example:
    python search_corpus.py \
        --archive "/path/to/pdf_archive" \
        --out     "./frankfurter_out" \
        --term "Felix Frankfurter" --term "Justice Frankfurter" \
        --exclude "Allgemeine Zeitung" --exclude "FAZ" \
        --workers 8 --context 200
"""
import argparse
import csv
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required:  pip install pymupdf")

try:
    from tqdm import tqdm
except ImportError:
    sys.exit("tqdm is required:  pip install tqdm")


def search_one(args):
    """Worker: search a single PDF. Returns (path, hits, had_text).

    hits is a list of dicts; had_text is False for scanned/untexted PDFs.
    Runs in a separate process, so PyMuPDF warning suppression is set here.
    """
    path, terms, excludes, context = args
    fitz.TOOLS.mupdf_display_errors(False)  # quiet noisy internal warnings
    hits = []
    had_text = False
    try:
        doc = fitz.open(path)
    except Exception:
        return path, hits, False  # treat as unreadable

    terms_l = [t.lower() for t in terms]
    excludes_l = [e.lower() for e in excludes]

    for pno in range(doc.page_count):
        try:
            text = doc.load_page(pno).get_text("text")
        except Exception:
            continue
        if text.strip():
            had_text = True
        low = text.lower()
        for term, term_l in zip(terms, terms_l):
            start = 0
            while True:
                i = low.find(term_l, start)
                if i == -1:
                    break
                lo = max(0, i - context)
                hi = min(len(text), i + len(term) + context)
                window = text[lo:hi]
                window_l = low[lo:hi]
                # disambiguation: skip if an exclusion term shares the window
                if any(e in window_l for e in excludes_l):
                    start = i + len(term_l)
                    continue
                snippet = " ".join(window.split())  # collapse whitespace
                hits.append({
                    "file": str(path),
                    "page": pno + 1,
                    "term": term,
                    "snippet": snippet,
                })
                start = i + len(term_l)
    doc.close()
    return path, hits, had_text


def main():
    ap = argparse.ArgumentParser(description="Parallel PDF corpus search with disambiguation.")
    ap.add_argument("--archive", required=True, help="Root folder of PDFs (searched recursively).")
    ap.add_argument("--out", required=True, help="Output folder (auto-created).")
    ap.add_argument("--term", action="append", required=True, help="Search term (repeatable).")
    ap.add_argument("--exclude", action="append", default=[], help="Exclusion term (repeatable).")
    ap.add_argument("--workers", type=int, default=8, help="Worker processes.")
    ap.add_argument("--context", type=int, default=200, help="Chars of context each side of a hit.")
    args = ap.parse_args()

    archive = Path(args.archive)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)  # auto-create output dir

    pdfs = sorted(archive.rglob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found under {archive}")
    print(f"Found {len(pdfs)} PDFs. Searching for {args.term} "
          f"(excluding {args.exclude or 'nothing'}) on {args.workers} workers.")

    tasks = [(p, args.term, args.exclude, args.context) for p in pdfs]
    all_hits, unreadable = [], []

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(search_one, t) for t in tasks]
        for fut in tqdm(as_completed(futures), total=len(futures), unit="pdf"):
            path, hits, had_text = fut.result()
            all_hits.extend(hits)
            if not had_text:
                unreadable.append(path)

    # matches.csv
    with (out / "matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "page", "term", "snippet"])
        w.writeheader()
        w.writerows(all_hits)

    # report.txt (grouped by file)
    by_file = {}
    for h in all_hits:
        by_file.setdefault(h["file"], []).append(h)
    with (out / "report.txt").open("w", encoding="utf-8") as f:
        f.write(f"Corpus search report\n{'=' * 50}\n")
        f.write(f"Archive : {archive}\nTerms   : {args.term}\n")
        f.write(f"Exclude : {args.exclude}\n")
        f.write(f"PDFs    : {len(pdfs)} | with hits: {len(by_file)} | "
                f"unreadable: {len(unreadable)} | total hits: {len(all_hits)}\n\n")
        for file, hits in sorted(by_file.items()):
            f.write(f"\n{file}  ({len(hits)} hit(s))\n{'-' * 50}\n")
            for h in hits:
                f.write(f"  p.{h['page']} [{h['term']}]  ...{h['snippet']}...\n")

    # unreadable.txt (OCR candidates)
    with (out / "unreadable.txt").open("w", encoding="utf-8") as f:
        for p in unreadable:
            f.write(f"{p}\n")

    print(f"\nDone. {len(all_hits)} hit(s) across {len(by_file)} file(s); "
          f"{len(unreadable)} unreadable (OCR candidates).")
    print(f"Output: {out.resolve()}")


if __name__ == "__main__":
    main()
