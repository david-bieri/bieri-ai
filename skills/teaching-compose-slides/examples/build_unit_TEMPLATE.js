// ============================================================================
// build_unit_TEMPLATE.js — scaffold for a new lecture unit's video decks
// ----------------------------------------------------------------------------
// Copy this file, rename it (e.g. build_week3.js), and replace the placeholder
// content. The reusable machinery lives in two bundled libraries — you only
// write CONTENT here, never slide-drawing code.
//
//   slide_lib.js    core builders (title/bullet/concept/threeBox/worked/news)
//   diagram_lib.js  theory diagrams (S/D, shifts, elasticity, supply fan) +
//                   empirics charts (addChart)
//
// THREE WAYS TO SHOW A CONCEPT — keep the tag grammar consistent:
//   · <concept>              theory diagram   (schematic, no units)
//   · In the data …          empirics / stylized-fact chart (real data + source)
//   · In the (macro-)news …  news hook        (article screenshot)
// A rich concept can run model → data → story (see the elasticity deck).
//
// NUMBERING: start `let n = 1` (the title slide is #1, unnumbered in the footer);
// pass `++n` to every other builder. Insert/reorder slides freely — numbers
// can't desync because they auto-increment in call order. Set `T` to the final
// slide count (run once; the QA step prints the actual count to confirm).
//
// Run:  NODE_PATH=$(npm root -g) node build_week3.js
// ============================================================================

const pptxgen = require("pptxgenjs");
const SL = require("./slide_lib.js");
const registerDiagrams = require("./diagram_lib.js");

// For a different course, override the footer once at the top:
// SL.setCourse({ courseLine: "UAP 4714: Urban Public Finance", profLine: "Prof. Bieri \u2013 Fall 2026" });

const {
  RED, DARK, BODY, GRAY, HELPERS,
  titleSlide, bulletSlide, conceptSlide, threeBoxSlide, workedSlide, newsSlide,
} = SL;

// ----------------------------------------------------------------------------
function buildDeck() {
  const p = new pptxgen();
  p.layout = "LAYOUT_16x9"; p.author = "David Bieri";
  p.title = "Week N V1 \u2014 <Topic>";

  let n = 1;                          // title slide is #1
  const D = registerDiagrams(p, HELPERS);   // diagram + chart builders
  const T = 9;                        // <-- final slide count (verify via QA print)

  // 1 — Title (no n/total; it's slide #1)
  titleSlide(p, "[L?.?] \u00b7 SU26  \u00b7  Week N",
    "<Deck title>",
    "<Module> \u00b7 Video x of y",
    "<Narration: open the deck. ~90\u2013150 words, 130 wpm.>");

  // 2 — Opening news hook (the puzzle)
  newsSlide(p, "[L?.?] \u00b7 In the (macro-)news \u2026",
    "<Headline>", "<Source (date)>", "<https://url>",
    "<Discussion question that the lecture will let them answer>",
    "<Narration: pose the puzzle; promise the tools to resolve it.>",
    ++n, T);

  // 3 — Learning outcomes
  bulletSlide(p, "[L?.?] \u00b7 Learning outcomes", "What you'll be able to do",
    [ "<outcome 1>", "<outcome 2>", "<outcome 3>", "<outcome 4>" ],
    "<Narration: the four things by the end.>",
    ++n, T);

  // 4 — Core content (bullets are telegraphic; the narration carries the prose)
  bulletSlide(p, "[L?.?] \u00b7 <Section>", "<Concept>",
    [ "<point 1>", "<point 2>", "<point 3>", "<point 4>" ],
    "<Narration.>",
    ++n, T);

  // 5 — THEORY diagram (schematic; pick the builder that fits)
  D.sdCrossSlide(p, "[L?.?] \u00b7 The model", "<Diagram title>",
    { equilibrium: true,            // sdCross opts: equilibrium, surplus, side[], caption
      side: [ { t: "<lead>", b: true, c: DARK, sa: 8 },
              { t: "<point>", c: BODY, bullet: true, sa: 6 } ],
      caption: "Theory diagram \u2014 stylized; axes are price (P) and quantity (Q)." },
    "<Narration: a theory diagram shows the logic, not a measurement.>",
    ++n, T);
  // other theory builders:
  //   D.shiftSlide(p, tag, title, { shift:"demand"|"supply", dir:"out"|"in", side, caption }, notes, ++n, T)
  //   D.elasticitySlopesSlide(p, tag, title, notes, ++n, T)
  //   D.supplyOverTimeSlide(p, tag, title, { side }, notes, ++n, T)

  // 6 — Worked example (formula -> given -> answer)
  workedSlide(p, "[L?.?] \u00b7 Worked example", "<What we compute>",
    "<FORMULA  =  numerator  \u00F7  denominator>",
    [ "<given 1>", "<given 2>", "<substitution \u2192 result>" ],
    "<RESULT  \u21D2  interpretation>",
    "<Narration: walk the arithmetic; tie to the assignment.>",
    ++n, T);

  // 7 — Three-box comparison / taxonomy
  threeBoxSlide(p, "[L?.?] \u00b7 <Section>", "<Three-way contrast>",
    [ { h: "<COL 1>", lines: ["<a>", "<b>", "<c>"] },
      { h: "<COL 2>", lines: ["<a>", "<b>", "<c>"] },
      { h: "<COL 3>", lines: ["<a>", "<b>", "<c>"] } ],
    "<Narration: read left to right.>",
    ++n, T);

  // 8 — EMPIRICS chart (real or stylized data; ALWAYS cite the source)
  D.chartSlide(p, "[L?.?] \u00b7 In the data \u2026", "<Chart title>",
    "line",                                   // "line" | "bar"
    [ { name: "<series>", labels: ["2021","2022","2023","2024","2025","2026"],
        values: [100, 108, 104, 99, 95, 92] } ],
    { colors: [RED], legend: false, ytitle: "<Y-axis label / index>" },
    "Stylized fact \u2014 illustrative. Source: <publisher (date)>.",   // source line
    "<Discussion question linking the data back to the theory diagram>",
    "<Narration: read the data through the model.>",
    ++n, T);

  // 9 — Recap
  bulletSlide(p, "[L?.?] \u00b7 Recap", "Key takeaways",
    [ "<takeaway 1>", "<takeaway 2>", "<takeaway 3>", "<next video / assignment>" ],
    "<Narration: pull it together; point ahead.>",
    ++n, T);

  return p;
}

// ----------------------------------------------------------------------------
// Build + QA (prints actual slide count so you can set T correctly)
(async () => {
  const p = buildDeck();
  const out = "Week N_<Topic>.pptx";
  await p.writeFile({ fileName: out });
  // QA: convert to PDF and rasterize a few slides for visual inspection
  //   python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf "<out>"
  //   pdftoppm -jpeg -r 100 "<pdf>" render/q
  console.log("wrote " + out);
})();
