# House Style Reference — Prof. Bieri Academic Lecture Decks

*Read this file before writing any pptxgenjs code.*

---

## Visual tokens

```javascript
const FONT = "Calibri";
const DARK = "262626";   // slide titles, dark body text
const BODY = "333333";   // standard body text
const GRAY = "808080";   // footer, captions, placeholders
const RED  = "C00000";   // lecture tags, accent bars, key terms
const BOX  = "D9D9D9";   // shaded content boxes (concept, worked-example)
const W = 10;            // slide width in inches (16:9 = 10 × 5.625)
const H = 5.625;         // slide height
```

---

## Slide layout

All slides: **white background (#FFFFFF)**, Calibri font throughout.

### Header zone (all content slides)
```
y=0.28   Tag line    fontSize:11  bold  color:RED    e.g. "[L2.1] · Characteristics"
y=0.54   Title       fontSize:26  bold  color:DARK   e.g. "Main characteristics"
```
Header occupies y=0 to y~1.35. Content starts at y=1.42.

### Content zone
```
y=1.42 to y=5.00   Available for slide body (bullets, boxes, charts)
```

### Footer zone (two-line format)
```
y=5.15   Line 1: "REAL/UAP 2004: Principles of Real Estate"  fontSize:8.5  color:GRAY
y=5.37   Line 2: "Prof. Bieri – {Semester}"                  fontSize:8.5  color:GRAY
right:   "{n}/{total}"                                        fontSize:8.5  color:GRAY  x=8.8
```
**Use the two-line footer with slide fraction.** Never use the old single-line footer
or a bare page number.

For non-REAL/UAP 2004 courses, replace line 1 with the appropriate course name.

---

## Tag format

Tags appear in the header zone, immediately above the slide title, in RED bold.

Format: `[Lecture code] · [Context label]`

Examples:
- `[L2.1] · Summer 2026`
- `[L2.1] · Characteristics`
- `[L2.1] · In the (micro-)news …`
- `[L9.2] · Step 2`
- `[L2.3e] · The ripple`

The lecture code always comes first. The context label describes what kind of slide
it is or its role in the sequence.

---

## Title slide

```
Red accent bar:   x=0.4  y=1.65  w=0.10  h=2.10  fill:#C00000
Lecture code:     x=0.65 y=1.70  fontSize:15  bold  color:RED
Big title:        x=0.65 y=2.10  fontSize:34  bold  color:DARK   (wraps OK)
Subtitle line:    x=0.65 y=3.38  fontSize:15  italic  color:BODY
                  e.g. "Real Estate Value Drivers · Week 1"
Footer note:      x=0.65 y=4.92  fontSize:10  color:GRAY
                  "REAL/UAP 2004: Principles of Real Estate · Prof. Bieri – Summer 2026"
```
Title slides do not carry the standard two-line footer — they have their own footer
treatment as above.

---

## Slide density rules

- **3–5 bullets** per content slide
- **No lead italic sentences** above bullets
- **Telegraphic phrases**, not full sentences — the narration carries the explanation
- Example: "Fixed location" not "Fixed location — it can't relocate to follow demand"
- Exception: concept boxes and equation slides use full sentences where needed for
  precision

---

## Shaded box dimensions

### Concept / equation box
```
Rectangle: x=0.9  y=1.42  w=8.2  h=3.72  fill:#D9D9D9
Text area:  x=1.1  y=1.57  w=7.8  h=3.42  align:center  valign:middle
```

### Worked-example formula box
```
Rectangle: x=0.4  y=1.38  w=9.2  h=0.90  fill:#D9D9D9
Formula:   x=0.6  y=1.42  w=8.8  h=0.82  fontSize:16  bold  align:center  valign:middle
```

### Three-box layout (for 3 boxes)
```
margin=0.4  gap=0.28  top=1.42  height=3.72
bw = (10 - 2×0.4 - 2×0.28) / 3 = 2.88"
Red header band: h=0.48  fill:#C00000  white bold text fontSize:13
Content area: starts at top+0.58
```

### News slide screenshot placeholder
```
Rectangle: x=0.4  y=1.38  w=9.2  h=3.14  fill:#D9D9D9
Placeholder text: centered italic gray  "[ Paste article screenshot here ]"
URL caption: y=4.58  fontSize:9  color:GRAY  italic
Discussion Q: y=4.90  fontSize:11.5  italic  preceded by red accent bar x=0.4 w=0.08 h=0.28
```

---

## Red accent bar (answer / highlight)

Used in worked-example slides to call out the answer:
```
Bar:    x=0.4  y=4.28  w=0.12  h=0.70  fill:#C00000
Text:   x=0.65 y=4.28  fontSize:16  bold  color:RED  valign:middle
```

---

## pptxgenjs environment

```javascript
const pptxgen = require("pptxgenjs");  // NODE_PATH=$(npm root -g) required
p.layout = "LAYOUT_16x9";
p.author = "David Bieri";
// Write: await pres.writeFile({ fileName: "/home/claude/DeckName.pptx" });
```
