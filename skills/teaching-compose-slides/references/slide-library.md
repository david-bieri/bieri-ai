# Slide Function Library — pptxgenjs

*Read house-style.md first, then use these functions.*

All functions share the signature pattern `(p, tag, title, ..., notes, n, total)`
where `p` is the pptxgen instance, `notes` is the speaker-note string, `n` is the
current slide number, and `total` is the deck's total slide count.

---

## Shared helpers

### `footer(s, n, total)`
Two-line footer with slide fraction. Call at end of every content slide.
```javascript
function footer(s, n, total) {
  s.addText("REAL/UAP 2004: Principles of Real Estate", {
    x: 0.4, y: 5.15, w: 8.5, h: 0.22,
    fontFace: FONT, fontSize: 8.5, color: GRAY, align: "left", margin: 0
  });
  s.addText("Prof. Bieri \u2013 Summer 2026", {
    x: 0.4, y: 5.37, w: 8.5, h: 0.22,
    fontFace: FONT, fontSize: 8.5, color: GRAY, align: "left", margin: 0
  });
  s.addText(`${n}/${total}`, {
    x: 8.8, y: 5.26, w: 0.78, h: 0.22,
    fontFace: FONT, fontSize: 8.5, color: GRAY, align: "right", margin: 0
  });
}
```
**Adapt line 2** for non-SU26 semesters and non-REAL/UAP 2004 courses.

### `header(p, s, tag, title)`
Red tag + bold title. Call at start of every content slide.
```javascript
function header(p, s, tag, title) {
  s.background = { color: "FFFFFF" };
  s.addText(tag, {
    x: 0.4, y: 0.28, w: 9.2, h: 0.28,
    fontFace: FONT, fontSize: 11, bold: true, color: RED, margin: 0
  });
  s.addText(title, {
    x: 0.4, y: 0.54, w: 9.2, h: 0.72,
    fontFace: FONT, fontSize: 26, bold: true, color: DARK, margin: 0
  });
}
```

---

## Slide types

### `titleSlide(p, lectureCode, title, subtitle, notes)`
Opening slide — red accent bar, no standard footer.
```javascript
function titleSlide(p, lectureCode, title, subtitle, notes) {
  const s = p.addSlide();
  s.background = { color: "FFFFFF" };
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 1.65, w: 0.1, h: 2.1, fill: { color: RED } });
  s.addText(lectureCode, { x: 0.65, y: 1.70, w: 8.8, h: 0.38,
    fontFace: FONT, fontSize: 15, bold: true, color: RED, margin: 0 });
  s.addText(title, { x: 0.65, y: 2.10, w: 8.8, h: 1.25,
    fontFace: FONT, fontSize: 34, bold: true, color: DARK, margin: 0 });
  s.addText(subtitle, { x: 0.65, y: 3.38, w: 8.8, h: 0.48,
    fontFace: FONT, fontSize: 15, color: BODY, italic: true, margin: 0 });
  s.addText("REAL/UAP 2004: Principles of Real Estate  \u00b7  Prof. Bieri \u2013 Summer 2026", {
    x: 0.65, y: 4.92, w: 8.8, h: 0.28,
    fontFace: FONT, fontSize: 10, color: GRAY, margin: 0 });
  if (notes) s.addNotes(notes);
  return s;
}
```

---

### `bulletSlide(p, tag, title, bullets, notes, n, total)`
Standard content slide — telegraphic phrase bullets, no lead sentence.
```javascript
function bulletSlide(p, tag, title, bullets, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  const items = bullets.map(b => ({
    text: b,
    options: { bullet: { indent: 18 }, breakLine: true,
               fontSize: 17, color: BODY, paraSpaceAfter: 10 }
  }));
  s.addText(items, { x: 0.5, y: 1.42, w: 9.1, h: 3.7, fontFace: FONT, valign: "top" });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}
```
**Bullet style:** 3–5 short phrases. Never full sentences. No italic lead above bullets.

---

### `conceptSlide(p, tag, title, lines, notes, n, total)`
Centered grey box for definitions, equations, or conceptual frameworks.

`lines` is an array of objects: `{ t: "text", s: fontSize, b: bold, i: italic, c: colorHex, sa: spaceAfter }`

Defaults: `s=18`, `b=false`, `i=false`, `c=DARK`, `sa=10`.
```javascript
function conceptSlide(p, tag, title, lines, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  const top = 1.42, bh = 3.72;
  s.addShape(p.shapes.RECTANGLE, { x: 0.9, y: top, w: 8.2, h: bh, fill: { color: BOX } });
  const items = lines.map(l => ({
    text: l.t,
    options: { breakLine: true, fontSize: l.s||18, bold:!!l.b, italic:!!l.i,
               color: l.c||DARK, align:"center", paraSpaceAfter: l.sa!=null?l.sa:10 }
  }));
  s.addText(items, { x: 1.1, y: top+0.15, w: 7.8, h: bh-0.3,
    fontFace: FONT, align:"center", valign:"middle" });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}
```

**Common patterns:**
- Formula: `{ t: "X = A / B", s: 22, b: true, c: RED }`
- Sub-note: `{ t: "interpretation text", s: 14, i: true, c: BODY }`
- Separator: `{ t: "+", s: 18, c: RED }`

---

### `threeBoxSlide(p, tag, title, boxes, notes, n, total)`
Three red-header grey boxes in a row.

`boxes` = array of `{ h: "HEADER TEXT", lines: ["bullet 1", "bullet 2", ...] }`
```javascript
function threeBoxSlide(p, tag, title, boxes, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  const gap = 0.28, marg = 0.4, top = 1.42;
  const bw = (W - 2*marg - 2*gap) / 3;  // ≈ 2.88"
  const bh = 3.72;
  boxes.forEach((b, i) => {
    const x = marg + i*(bw+gap);
    s.addShape(p.shapes.RECTANGLE, { x, y: top, w: bw, h: bh, fill: { color: BOX } });
    s.addShape(p.shapes.RECTANGLE, { x, y: top, w: bw, h: 0.48, fill: { color: RED } });
    s.addText(b.h, { x: x+0.1, y: top+0.01, w: bw-0.2, h: 0.46,
      fontFace: FONT, fontSize: 13, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0 });
    const items = b.lines.map(l => ({
      text: l, options: { bullet: { indent: 12 }, breakLine: true,
                          fontSize: 12, color: BODY, paraSpaceAfter: 5 }
    }));
    s.addText(items, { x: x+0.15, y: top+0.58, w: bw-0.3, h: bh-0.68,
      fontFace: FONT, valign: "top" });
  });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}
```
Use for: value types, market phases, stakeholder groups, property type comparisons.

---

### `workedSlide(p, tag, title, formula, given, answer, notes, n, total)`
Formula box + given values + red-bar answer. For quantitative step-by-step examples.

- `formula`: string displayed in the grey formula box (centred, bold)
- `given`: array of strings (bullet list of given values)
- `answer`: string displayed in red answer bar
```javascript
function workedSlide(p, tag, title, formula, given, answer, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  // Formula box
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 1.38, w: 9.2, h: 0.9, fill: { color: BOX } });
  s.addText(formula, { x: 0.6, y: 1.42, w: 8.8, h: 0.82,
    fontFace: FONT, fontSize: 16, bold: true, color: DARK,
    align: "center", valign: "middle", margin: 0 });
  // Given values
  const gItems = given.map(l => ({
    text: l, options: { bullet: { indent: 16 }, breakLine: true,
                        fontSize: 15, color: BODY, paraSpaceAfter: 6 }
  }));
  s.addText(gItems, { x: 0.5, y: 2.42, w: 9.1, h: 1.72, fontFace: FONT, valign: "top" });
  // Answer bar
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 4.28, w: 0.12, h: 0.7, fill: { color: RED } });
  s.addText(answer, { x: 0.65, y: 4.28, w: 8.9, h: 0.7,
    fontFace: FONT, fontSize: 16, bold: true, color: RED, valign: "middle", margin: 0 });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}
```
**Dimensional integrity rule:** always verify units in both the formula and the
answer. See `teaching:video-scripts` for narration conventions on worked examples.

---

### `newsSlide(p, tag, title, source, url, question, notes, n, total)`
Image-forward "In the news" slide. See `teaching:news-hooks` for content guidance.

- `tag`: includes the variant — e.g., `"[L2.3] · In the (micro-)news …"`
- `title`: article headline (≤10 words)
- `source`: `"Publication / Author (Month Year)"`
- `url`: full URL
- `question`: single discussion prompt (displayed on slide, ~15 words)
- `notes`: ~100-word narration note
```javascript
function newsSlide(p, tag, title, source, url, question, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  // Screenshot placeholder
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 1.38, w: 9.2, h: 3.14, fill: { color: BOX } });
  s.addText("[ Paste article screenshot here ]", {
    x: 0.5, y: 2.77, w: 9.0, h: 0.4,
    fontFace: FONT, fontSize: 13, italic: true, color: GRAY, align: "center", margin: 0 });
  // URL caption
  s.addText(`${source}  \u00b7  ${url}`, {
    x: 0.4, y: 4.58, w: 9.2, h: 0.26,
    fontFace: FONT, fontSize: 9, color: GRAY, italic: true, margin: 0 });
  // Discussion question with red accent bar
  if (question) {
    s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 4.90, w: 0.08, h: 0.28, fill: { color: RED } });
    s.addText(question, {
      x: 0.6, y: 4.90, w: 9.0, h: 0.28,
      fontFace: FONT, fontSize: 11.5, color: DARK, italic: true, valign: "middle", margin: 0 });
  }
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}
```

---

## Build script skeleton

```javascript
const pptxgen = require("pptxgenjs");
// paste FONT/DARK/BODY/GRAY/RED/BOX/W constants here
// paste footer(), header(), and required slide functions here

function buildDeck() {
  const p = new pptxgen();
  p.layout = "LAYOUT_16x9";
  p.author = "David Bieri";
  p.title = "Deck Title";
  const T = 14;  // total slides — hardcode after planning

  titleSlide(p, "[L2.1] · SU26", "Slide Title", "Course · Week N", "notes...");
  bulletSlide(p, "[L2.1] · Topic", "Slide Title", ["bullet 1", "bullet 2"], "notes...", 2, T);
  // ... remaining slides

  return p;
}

(async () => {
  const pres = buildDeck();
  await pres.writeFile({ fileName: "/home/claude/DeckName.pptx" });
  console.log("wrote DeckName.pptx");
})();
```
