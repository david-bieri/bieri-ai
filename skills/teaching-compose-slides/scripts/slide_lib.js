// ============================================================================
// slide_lib.js — core lecture-deck slide builders (Bieri house style)
// Bundled resource of teaching-compose-slides. Pairs with diagram_lib.js.
// Reusable across courses: call setCourse() to change the footer strings.
//
//   const SL = require("./slide_lib.js");
//   SL.setCourse({ courseLine: "UAP 4714: Urban Public Finance", profLine: "Prof. Bieri \u2013 Fall 2026" });
//   const { titleSlide, bulletSlide, conceptSlide, threeBoxSlide,
//           workedSlide, newsSlide, HELPERS, RED, DARK, BODY, GRAY } = SL;
// ============================================================================

// ---- Visual tokens (house-style.md) ----
const FONT = "Calibri";
const DARK = "262626";
const BODY = "333333";
const GRAY = "808080";
const RED  = "C00000";
const BOX  = "D9D9D9";
const W = 10, H = 5.625;

// ---- Course config (override per course via setCourse) ----
const COURSE = {
  courseLine: "REAL/UAP 2004: Principles of Real Estate",
  profLine:   "Prof. Bieri \u2013 Summer 2026",
};
function setCourse(opts = {}) { Object.assign(COURSE, opts); }

// ---- Shared helpers ----
function footer(s, n, total) {
  s.addText(COURSE.courseLine, {
    x: 0.4, y: 5.15, w: 8.5, h: 0.22,
    fontFace: FONT, fontSize: 8.5, color: GRAY, align: "left", margin: 0 });
  s.addText(COURSE.profLine, {
    x: 0.4, y: 5.37, w: 8.5, h: 0.22,
    fontFace: FONT, fontSize: 8.5, color: GRAY, align: "left", margin: 0 });
  s.addText(`${n}/${total}`, {
    x: 8.8, y: 5.26, w: 0.78, h: 0.22,
    fontFace: FONT, fontSize: 8.5, color: GRAY, align: "right", margin: 0 });
}

function header(p, s, tag, title) {
  s.background = { color: "FFFFFF" };
  s.addText(tag, { x: 0.4, y: 0.28, w: 9.2, h: 0.28,
    fontFace: FONT, fontSize: 11, bold: true, color: RED, margin: 0 });
  s.addText(title, { x: 0.4, y: 0.54, w: 9.2, h: 0.72,
    fontFace: FONT, fontSize: 26, bold: true, color: DARK, margin: 0 });
}

// Shared helper bundle passed to the diagram/chart library (registerDiagrams)
const HELPERS = { FONT, DARK, BODY, GRAY, RED, BOX, header, footer };

// ---- Slide types ----
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
  s.addText(`${COURSE.courseLine}  \u00b7  ${COURSE.profLine}`, {
    x: 0.65, y: 4.92, w: 8.8, h: 0.28, fontFace: FONT, fontSize: 10, color: GRAY, margin: 0 });
  if (notes) s.addNotes(notes);
  return s;
}

function bulletSlide(p, tag, title, bullets, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  const items = bullets.map(b => ({
    text: b, options: { bullet: { indent: 18 }, breakLine: true,
      fontSize: 17, color: BODY, paraSpaceAfter: 10 } }));
  s.addText(items, { x: 0.5, y: 1.42, w: 9.1, h: 3.7, fontFace: FONT, valign: "top" });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}

function conceptSlide(p, tag, title, lines, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  const top = 1.42, bh = 3.72;
  s.addShape(p.shapes.RECTANGLE, { x: 0.9, y: top, w: 8.2, h: bh, fill: { color: BOX } });
  const items = lines.map(l => ({
    text: l.t, options: { breakLine: true, fontSize: l.s||18, bold:!!l.b, italic:!!l.i,
      color: l.c||DARK, align:"center", paraSpaceAfter: l.sa!=null?l.sa:10 } }));
  s.addText(items, { x: 1.1, y: top+0.15, w: 7.8, h: bh-0.3,
    fontFace: FONT, align:"center", valign:"middle" });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}

function threeBoxSlide(p, tag, title, boxes, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  const gap = 0.28, marg = 0.4, top = 1.42;
  const bw = (W - 2*marg - 2*gap) / 3;
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
        fontSize: 12, color: BODY, paraSpaceAfter: 5 } }));
    s.addText(items, { x: x+0.15, y: top+0.58, w: bw-0.3, h: bh-0.68,
      fontFace: FONT, valign: "top" });
  });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}

function workedSlide(p, tag, title, formula, given, answer, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 1.38, w: 9.2, h: 0.9, fill: { color: BOX } });
  s.addText(formula, { x: 0.6, y: 1.42, w: 8.8, h: 0.82,
    fontFace: FONT, fontSize: 16, bold: true, color: DARK,
    align: "center", valign: "middle", margin: 0 });
  const gItems = given.map(l => ({
    text: l, options: { bullet: { indent: 16 }, breakLine: true,
      fontSize: 15, color: BODY, paraSpaceAfter: 6 } }));
  s.addText(gItems, { x: 0.5, y: 2.42, w: 9.1, h: 1.72, fontFace: FONT, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 4.28, w: 0.12, h: 0.7, fill: { color: RED } });
  s.addText(answer, { x: 0.65, y: 4.28, w: 8.9, h: 0.7,
    fontFace: FONT, fontSize: 16, bold: true, color: RED, valign: "middle", margin: 0 });
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}

function newsSlide(p, tag, title, source, url, question, notes, n, total) {
  const s = p.addSlide();
  header(p, s, tag, title);
  s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 1.38, w: 9.2, h: 2.92, fill: { color: BOX } });
  s.addText("[ Paste article screenshot here ]", {
    x: 0.5, y: 2.66, w: 9.0, h: 0.4,
    fontFace: FONT, fontSize: 13, italic: true, color: GRAY, align: "center", margin: 0 });
  s.addText(`${source}  \u00b7  ${url}`, {
    x: 0.4, y: 4.40, w: 9.2, h: 0.24,
    fontFace: FONT, fontSize: 9, color: GRAY, italic: true, margin: 0 });
  if (question) {
    s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 4.70, w: 0.08, h: 0.30, fill: { color: RED } });
    s.addText(question, { x: 0.6, y: 4.68, w: 9.0, h: 0.34,
      fontFace: FONT, fontSize: 11.5, color: DARK, italic: true, valign: "middle", margin: 0 });
  }
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}

// ---- v1.2.0 embed path: figure slide with caption pulled from captions.json ----
// captions.json is produced from captions.yaml by figures.dump_json() (Makefile step).
const fs = require("fs");
const path = require("path");
function loadCaptions(jsonPath) {
  const fp = jsonPath || path.join(__dirname, "captions.json");
  try { return JSON.parse(fs.readFileSync(fp, "utf8")); }
  catch (e) { return {}; }
}

// Embed a figure image (PNG from the diagram/chart build) and pull its title +
// source line from captions.json by key. Slide carries the caption (caption_mode=off).
function figureSlide(p, tag, key, imagePath, notes, n, total, opts) {
  const o = opts || {};
  const caps = o.captions || loadCaptions(o.captionsPath);
  const rec = caps[key] || {};
  const title = o.title || rec.short || key;
  const source = (o.source != null) ? o.source : (rec.source || "");
  const s = p.addSlide();
  header(p, s, tag, title);
  // center the image in the content area, preserving aspect via "contain"
  s.addImage({ path: imagePath, x: 0.7, y: 1.45, w: 8.6, h: 3.1, sizing: { type: "contain", w: 8.6, h: 3.1 } });
  if (source) {
    s.addText(source, { x: 0.4, y: 4.66, w: 9.2, h: 0.26,
      fontFace: FONT, fontSize: 9.5, italic: true, color: GRAY, margin: 0 });
  }
  footer(s, n, total);
  if (notes) s.addNotes(notes);
  return s;
}

module.exports = {
  // tokens
  FONT, DARK, BODY, GRAY, RED, BOX, W, H,
  // config
  setCourse, COURSE,
  // primitives
  header, footer, HELPERS, loadCaptions,
  // slide builders
  titleSlide, bulletSlide, conceptSlide, threeBoxSlide, workedSlide, newsSlide, figureSlide,
};
