# webdev:latex-pdf-guide

This skill defines the workflow for maintaining formal documentation (User Guides, Manuals) written in LaTeX, compiling them to PDF, and exposing them on a web frontend with proper citation instructions.

## When to invoke

Trigger on: "update the user guide", "compile the LaTeX to PDF", "publish the manual on the site", "sync the docs to the new features", "edit the .tex source", or any formal LaTeX documentation or PDF web-delivery work. Invoked by `webdev:release-workflow` at Step 2.

---

## 1. LaTeX Compilation Workflow

Documentation should be maintained in a `.tex` source file. When features change, the `.tex` file MUST be updated and recompiled.

### Compilation Commands

Run `pdflatex` twice to ensure the Table of Contents and references resolve correctly:

```bash
pdflatex -interaction=nonstopmode Guide.tex
pdflatex -interaction=nonstopmode Guide.tex
```

### Unicode Handling

`pdflatex` does not natively support modern Unicode emojis or certain special characters. If you encounter `Unicode character` errors during compilation:
1. Replace emojis with LaTeX equivalents (e.g., `$\rightarrow$` instead of an arrow emoji).
2. Ensure `\usepackage[utf8]{inputenc}` and `\usepackage[T1]{fontenc}` are included in the preamble.

### Cleanup

Always remove auxiliary files after a successful compilation:

```bash
rm -f Guide.aux Guide.log Guide.out Guide.toc
```

## 2. Web Integration

The compiled PDF should be linked from a dedicated HTML guide page.

**Download Button Pattern:**
```html
<a href="Guide.pdf" class="btn btn-primary" download>
  PDF herunterladen (Download PDF)
</a>
```

## 3. Academic Citation Pattern

For academic or research projects, provide a "How to Cite" section at the bottom of the guide page and link to it from the global site footer (see `static-site-i18n` for footer propagation rules).

**HTML Citation Block Template:**

```html
<section id="citation" class="citation-section">
  <h2 data-i18n="guide_cite_title">Zitierweise / How to Cite</h2>
  
  <div class="cite-block">
    <h4>APA</h4>
    <p style="user-select: all;">Author, A. (Year). <em>Title</em> [Interactive web application]. Publisher. https://example.com/</p>
  </div>
  
  <div class="cite-block">
    <h4>BibTeX</h4>
    <pre style="user-select: all;"><code>@misc{key,
  author = {Author, A.},
  title = {Title},
  year = {2026},
  howpublished = {\url{https://example.com/}}
}</code></pre>
  </div>
</section>
```

*The `user-select: all` style allows one-click copy of the full citation.*

## 4. Syncing Rule

Whenever a new feature is added to the web application:
1. Document it in the web UI (guide page).
2. Document it in the LaTeX source (`.tex`).
3. Recompile the PDF.
4. Commit the `.html`, `.tex`, and `.pdf` files together in a single atomic commit.

## Related Skills

| Need | Skill |
|------|-------|
| Footer link to citation section | `static-site-i18n` (Section 2: Propagation Rule) |
| Full release ceremony that includes doc sync | `web-release-workflow` (Step 2) |
