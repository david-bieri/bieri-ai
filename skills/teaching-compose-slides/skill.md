
# course:compose-slides

## When to invoke

Trigger on: "build the deck"; "generate slides"; "narration-ready deck";
"add slides to the series"; "my style" or "house style"; mentions pptxgenjs;
any request to produce a .pptx from course content; "Summer/Spring 2026 slides".
Always read references/house-style.md and references/slide-library.md first.

---

Builds lecture decks in Prof. Bieri's house style. Works across all courses.

---

## Before writing any code

**Always read both reference files first:**

1. `references/house-style.md` — visual tokens, footer spec, tag format, slide
   density rules. Read this first, every time.
2. `references/slide-library.md` — complete pptxgenjs function library with
   signatures and examples. Read before writing any slide functions.

These files are authoritative. Do not rely on memory for token values or function
signatures — they are updated when the style evolves.

---

## Workflow

### Step 1 — Gather inputs

From context or by asking:
- **Course** (REAL/UAP 2004, UAP 4714, UAP 5174, executive program, other)
- **Lecture/module code** (e.g., `L2.1`, `L9.3`, `W3`, or executive session label)
- **Semester** (Spring 2026, Summer 2026, Fall 2026, etc.)
- **Content source** — KB search results, uploaded slides, user-provided outline,
  or KB + new material combined
- **Video deck or in-person deck** — affects slide density and whether narration
  notes are needed (see `course:video-scripts` for full narration guidance)
- **Slide count target** (default: 12–14 for a 10-min video; 20–30 for a full lecture)

### Step 2 — Search project knowledge (if available)

If the course KB is in Project knowledge, always search before writing content:
```
project_knowledge_search("topic or concept name")
```
Use KB results to anchor content — prefer David's own formulations over generic
textbook language. Note the KB source slide tag for reference.

### Step 3 — Plan the deck structure

Sketch the slide sequence before writing code:
```
1. Title
2. [NEWS] Opening hook
3. [LO] Learning outcomes
4–N. Content slides (bullets, concepts, worked examples, three-box)
N+1. [NEWS] Closing hook
N+2. [LO] Key takeaways / recap
```
Present the outline to the user for confirmation before generating code if the
deck is more than ~10 slides or the content is novel.

### Step 4 — Write pptxgenjs code

Read `references/slide-library.md`, then write using the standard function library.
One build script per deck, output to `/home/claude/DeckName.pptx`.

### Step 5 — Render and QA

```bash
export NODE_PATH=$(npm root -g)
node build_deck.js

# Convert to PDF for visual QA
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf DeckName.pptx
pdftoppm -jpeg -r 110 DeckName.pdf render/DeckName

# Inspect key slides
```
QA at minimum: title slide, one content slide, one three-box, one news hook,
one worked example (if present), recap slide.

### Step 6 — Deliver

Copy to `/mnt/user-data/outputs/` and call `present_files`.

---

## Slide density — telegraphic style

This is the single most important style rule:

**Bullets are anchor phrases, not sentences.**

| Too verbose | Correct |
|-------------|---------|
| "Fixed location — it can't relocate to follow demand" | "Fixed location" |
| "Buyer and seller are typically motivated — no duress" | "Buyer & seller: typically motivated" |
| "Linkages are the connections between a property and the places its users need to go" | "Connections between property and places users need" |

- 3–5 bullets per slide maximum
- No italic "lead" sentence above bullets
- No explanatory clause after an em-dash unless essential
- The narration note carries all explanation

---

## News hook slides — see `course:news-hooks`

For any deck that needs "In the news" slides, invoke `course:news-hooks` to
find stories and format them. The news slide format is defined in
`references/slide-library.md` under `newsSlide()`.

---

## Multi-deck series

For a series (e.g., four Week-1 videos), build all decks from a single script
using separate video functions. Keep the total slide counts per deck to 12–14.
Number slides as fractions (`n/total`) — the total is hardcoded per deck.

---

## Course-specific tag conventions

| Course | Tag format | Example |
|--------|-----------|---------|
| REAL/UAP 2004 — spring/fall | `[L{mod}.{lec}] · {Semester}` | `[L2.1] · Spring 2026` |
| REAL/UAP 2004 — summer | `[L{mod}.{lec}] · SU26` | `[L2.3] · SU26` |
| UAP/ECON 4714 | `[L{mod}.{lec}] · {Semester}` | `[L4.2] · Fall 2026` |
| UAP 5174 | `[L{n}] · {Semester}` | `[L7] · Fall 2026` |
| Executive programs | `[Session {n}]` | `[Session 3]` |

When the course is REAL/UAP 2004 Summer, also append the week:
`[L2.1] · SU26  ·  Week 1`

---

## Environment notes

- pptxgenjs@4.0.1 installed globally at `/home/claude` (Node.js)
- `export NODE_PATH=$(npm root -g)` required before running scripts
- soffice available for PDF conversion; pdftoppm for rasterisation
- Output directory: `/mnt/user-data/outputs/`
