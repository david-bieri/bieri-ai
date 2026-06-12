
# teaching:video-scripts

## When to invoke

Trigger on: "write the narration"; "script for the video"; "speaking notes";
"Loom script"; "teleprompter text"; "how long will this take to record";
"embed notes into the deck"; timing a script to a target length.
Always use this skill — do not freestyle narration without its calibration.

---

Generates slide-level narration scripts for asynchronous lecture videos, calibrated
to Prof. Bieri's recording pace and embedded as PPTX speaker notes.

---

## Timing calibration

| Target | Words |
|--------|-------|
| 10 min | ~1,300 words |
| 11 min | ~1,430 words |
| 12 min | ~1,560 words |

- **Speaking pace:** 130 wpm (comfortable academic narration, not rushed)
- **Per-slide target:** 90–130 words for a standard content slide
- **Title slide:** 60–80 words (brief welcome + roadmap)
- **Concept/equation slides:** 100–140 words (formula needs time)
- **Worked-example slides:** 120–150 words (walk arithmetic step by step)
- **News hook slides:** 90–110 words (story framing + concept connection)
- **Recap slides:** 80–100 words (synthesis + bridge to next video)

After writing all notes, compute total word count and report `~N words · ~M min`.

---

## Note structure by slide type

### Title slide
```
Welcome framing (course + video number if series)
→ Brief roadmap: "In this video we'll cover X, Y, and Z"
→ Why it matters / motivation sentence
→ Invitation to watch
```

### Content / bullet slide
```
Connect to prior slide (1 sentence)
→ Explain the concept in plain language
→ Give a concrete example or analogy
→ State the key implication
→ Bridge to next slide
```
**Do not read bullets verbatim.** Paraphrase and expand. The bullets are
anchor points for the viewer; the narration is the explanation.

### Concept / equation slide
```
Name and define the concept
→ Explain the logic behind it
→ Walk through the formula or structure left-to-right
→ Interpret: what does a high/low value mean?
→ Foreshadow the worked example
```

### Worked-example slide
```
State what you're about to calculate
→ Name each given value and its units ("8,000 construction jobs…")
→ State the operation explicitly ("divide the regional share by the national share")
→ State the result with units ("a location quotient of 3.27")
→ Interpret: what does this number mean in context?
→ Bridge to next step
```
**Dimensional integrity:** always name units when introducing numbers.
Verify that the arithmetic in the note matches the formula on the slide.

### Three-box / comparison slide
```
Introduce the framework ("Three groups / types / phases")
→ Walk left-to-right through the boxes, 1–2 sentences each
→ State the relationship or contrast between boxes
→ Draw the implication for valuation / analysis
```

### News hook slide
```
One sentence framing the story
→ State the key figure or finding (cite the source)
→ Connect explicitly to the concept covered in adjacent slides
→ Pose the discussion question as a genuine puzzle
```

### Recap / takeaways slide
```
"Let's bring it together" or equivalent
→ Restate each takeaway in one sentence (not verbatim from bullet)
→ If series: bridge to the next video with a teaser
→ If final: brief closing
```

---

## Output formats

### Embedded in PPTX (primary)
Speaker notes are added to each slide via `slide.addNotes(noteText)` in pptxgenjs,
or manually pasted into PowerPoint's Notes pane.

### Combined Markdown document (secondary)
When the user wants a standalone script document:

```markdown
# [Video Title] — Narration Script

*[Deck tag] · [N] slides · ~[W] words · ~[M] min*

---

**Slide 1 — [Title]**

[Note text]

---

**Slide 2 — [Title]**

[Note text]
```

Both formats should be produced together unless the user specifies otherwise.

---

## Style conventions

- **Academic but accessible:** use the vocabulary of the course, but explain jargon
  on first use
- **First-person, direct:** "Let's start with…", "Notice that…", "Here's the key…"
- **Avoid:** "In this slide we see…" — describe the concept, not the slide
- **Avoid:** reading bullet text verbatim — paraphrase always
- **Analogies and real-world examples** should connect to the news hook where possible
- **Pronounce numbers:** write "three hundred" not "300" in notes (for teleprompter use)
- **Formulae:** read left-to-right, name each term ("EBM equals total employment
  divided by basic employment")

---

## QA checklist

After drafting all notes:

- [ ] Total word count computed and reported
- [ ] No slide over 160 words (overflow risk on long-form takes)
- [ ] No worked-example note that reads the formula without interpreting it
- [ ] No recap note that just lists the bullet text verbatim
- [ ] Arithmetic in all worked-example notes verified against slide formula
- [ ] News hook notes contain a specific quantitative claim (not just a vague reference)
- [ ] Opening and closing notes frame the video as a coherent unit

---

## Recording tools

- **Primary:** Loom (preferred for async delivery, direct Canvas integration)
- **Teleprompter:** QPrompt (Windows-native; paste notes text)
- **Backup:** Zoom with local recording

QPrompt tip: paste the combined Markdown script, set scroll speed to match ~130 wpm,
and use the lecture slides as the visual background.
