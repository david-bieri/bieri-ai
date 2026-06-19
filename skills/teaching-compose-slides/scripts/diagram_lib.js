// ============================================================================
// diagram_lib.js — THEORY diagrams + EMPIRICS charts for Bieri lecture decks
// Extends the compose-slides slide library. Two families:
//   THEORY   → schematic curves drawn with native vector LINE shapes
//   EMPIRICS → real / stylized-fact data via native addChart
// House tokens: Demand = DARK, Supply = RED, guides = GRAY, accents = RED.
// Exposes: registerDiagrams(p, helpers) returning the diagram/chart builders.
// ============================================================================

module.exports = function registerDiagrams(p, H) {
  const { FONT, DARK, BODY, GRAY, RED, BOX, header, footer } = H;

  // ---- low-level: draw a straight segment between two points (handles flip) ----
  function seg(s, x1, y1, x2, y2, opt = {}) {
    const x = Math.min(x1, x2), y = Math.min(y1, y2);
    const w = Math.abs(x2 - x1) || 0.0001, h = Math.abs(y2 - y1) || 0.0001;
    s.addShape(p.shapes.LINE, {
      x, y, w, h, flipH: (x2 < x1), flipV: (y2 < y1),
      line: { color: opt.color || DARK, width: opt.width || 2.25,
              dashType: opt.dash || "solid",
              beginArrowType: opt.beginArrow || "none",
              endArrowType: opt.endArrow || "none" } });
  }

  // ---- a plot frame with mapped coordinates (qx,py in 0..1) ----
  // Returns { X, Y, axes } where X(qx),Y(py) map normalized coords to inches.
  function plot(s, ox, oy, pw, ph, xlab, ylab) {
    // axes (L-shape) with arrowheads
    seg(s, ox, oy, ox, oy - ph, { color: DARK, width: 1.75, endArrow: "triangle" }); // Y up
    seg(s, ox, oy, ox + pw, oy, { color: DARK, width: 1.75, endArrow: "triangle" }); // X right
    if (ylab) s.addText(ylab, { x: ox - 0.55, y: oy - ph - 0.05, w: 0.9, h: 0.3,
      fontFace: FONT, fontSize: 13, bold: true, color: DARK, align: "left", margin: 0 });
    if (xlab) s.addText(xlab, { x: ox + pw - 0.35, y: oy + 0.06, w: 1.2, h: 0.3,
      fontFace: FONT, fontSize: 13, bold: true, color: DARK, align: "left", margin: 0 });
    s.addText("0", { x: ox - 0.28, y: oy - 0.02, w: 0.24, h: 0.22,
      fontFace: FONT, fontSize: 10, color: GRAY, align: "right", margin: 0 });
    const X = qx => ox + qx * pw;
    const Y = py => oy - py * ph;
    return { X, Y };
  }

  function curveLabel(s, x, y, txt, color) {
    s.addText(txt, { x: x - 0.05, y: y - 0.13, w: 0.95, h: 0.26,
      fontFace: FONT, fontSize: 13, bold: true, italic: true, color: color || DARK,
      align: "left", valign: "middle", margin: 0 });
  }

  function dot(s, x, y, color) {
    s.addShape(p.shapes.OVAL, { x: x - 0.045, y: y - 0.045, w: 0.09, h: 0.09,
      fill: { color: color || RED }, line: { color: color || RED, width: 1 } });
  }

  // caption line (source / note) shared by theory + empirics
  function caption(s, txt) {
    s.addText(txt, { x: 0.4, y: 4.62, w: 9.2, h: 0.26,
      fontFace: FONT, fontSize: 9.5, italic: true, color: GRAY, margin: 0 });
  }

  // side-note panel (right of a left-placed diagram): array of {t,b,c}
  function sideNote(s, x, lines) {
    const items = lines.map(l => ({ text: l.t, options: {
      breakLine: true, bullet: l.bullet ? { indent: 14 } : false,
      fontSize: l.s || 14, bold: !!l.b, italic: !!l.i, color: l.c || BODY,
      paraSpaceAfter: l.sa != null ? l.sa : 8 } }));
    s.addText(items, { x, y: 1.55, w: 9.55 - x, h: 3.0, fontFace: FONT, valign: "top" });
  }

  // ========================================================================
  // THEORY DIAGRAM 1 — Supply & Demand (two curves; optional equilibrium)
  // ========================================================================
  function sdCrossSlide(p, tag, title, opts, notes, n, total) {
    const o = opts || {};
    const s = p.addSlide(); header(p, s, tag, title);
    const ox = 1.1, oy = 4.35, pw = 4.7, ph = 2.75;
    const { X, Y } = plot(s, ox, oy, pw, ph, "Q", "P");
    // demand: down-sloping (dark)
    seg(s, X(0.05), Y(0.92), X(0.95), Y(0.10), { color: DARK, width: 2.5 });
    curveLabel(s, X(0.95) + 0.04, Y(0.10), "D", DARK);
    // supply: up-sloping (red)
    seg(s, X(0.05), Y(0.10), X(0.95), Y(0.92), { color: RED, width: 2.5 });
    curveLabel(s, X(0.95) + 0.04, Y(0.92), "S", RED);
    if (o.equilibrium) {
      // intersection at center (0.5,0.5)
      dot(s, X(0.5), Y(0.5), RED);
      seg(s, X(0.5), Y(0.5), X(0.5), Y(0), { color: GRAY, width: 1, dash: "dash" });
      seg(s, X(0.5), Y(0.5), X(0), Y(0.5), { color: GRAY, width: 1, dash: "dash" });
      s.addText("P*", { x: X(0) - 0.42, y: Y(0.5) - 0.11, w: 0.4, h: 0.22,
        fontFace: FONT, fontSize: 12, bold: true, color: RED, align: "right", margin: 0 });
      s.addText("Q*", { x: X(0.5) - 0.2, y: Y(0) + 0.04, w: 0.4, h: 0.22,
        fontFace: FONT, fontSize: 12, bold: true, color: RED, align: "center", margin: 0 });
    }
    if (o.surplus) { // shade/label surplus above P* and shortage below
      s.addText("surplus  (P > P*)", { x: X(0.18), y: Y(0.86), w: 1.9, h: 0.22,
        fontFace: FONT, fontSize: 10, italic: true, color: GRAY, margin: 0 });
      s.addText("shortage  (P < P*)", { x: X(0.18), y: Y(0.18), w: 1.9, h: 0.22,
        fontFace: FONT, fontSize: 10, italic: true, color: GRAY, margin: 0 });
    }
    if (o.side) sideNote(s, 6.3, o.side);
    if (o.caption) caption(s, o.caption);
    footer(s, n, total); if (notes) s.addNotes(notes);
    return s;
  }

  // ========================================================================
  // THEORY DIAGRAM 2 — A shift (D1->D2 or S1->S2) with two equilibria
  // opts: { shift:"demand"|"supply", dir:"out"|"in" }
  // ========================================================================
  function shiftSlide(p, tag, title, opts, notes, n, total) {
    const o = opts || {};
    const s = p.addSlide(); header(p, s, tag, title);
    const ox = 1.1, oy = 4.35, pw = 4.7, ph = 2.75;
    const { X, Y } = plot(s, ox, oy, pw, ph, "Q", "P");
    const dShift = (o.shift === "demand");
    const out = (o.dir !== "in"); // default outward
    if (dShift) {
      // fixed supply (red)
      seg(s, X(0.05), Y(0.08), X(0.95), Y(0.92), { color: RED, width: 2.5 });
      curveLabel(s, X(0.95) + 0.04, Y(0.92), "S", RED);
      // D1 and D2 (dark; D2 shifted right if out)
      const off = out ? 0.22 : -0.22;
      seg(s, X(0.02), Y(0.78), X(0.78), Y(0.04), { color: DARK, width: 2.2 });
      curveLabel(s, X(0.78) + 0.02, Y(0.04), "D\u2081", DARK);
      seg(s, X(0.02 + off), Y(0.78 + (out ? 0.16 : -0.16)), X(0.78 + off), Y(0.04 + (out ? 0.18 : -0.18)),
        { color: DARK, width: 2.2, dash: "dash" });
      curveLabel(s, X(0.78 + off) + 0.02, Y(0.04 + (out ? 0.18 : -0.18)), "D\u2082", DARK);
      // two equilibria
      dot(s, X(0.40), Y(0.40), GRAY); dot(s, X(0.55), Y(0.55), RED);
      seg(s, X(0.40), Y(0.40), X(0), Y(0.40), { color: GRAY, width: 0.75, dash: "dash" });
      seg(s, X(0.55), Y(0.55), X(0), Y(0.55), { color: GRAY, width: 0.75, dash: "dash" });
      s.addText(out ? "P \u2191 , Q \u2191" : "P \u2193 , Q \u2193",
        { x: 6.3, y: 3.5, w: 3.2, h: 0.4, fontFace: FONT, fontSize: 16, bold: true,
          color: RED, margin: 0 });
    } else {
      // fixed demand (dark)
      seg(s, X(0.05), Y(0.92), X(0.95), Y(0.08), { color: DARK, width: 2.5 });
      curveLabel(s, X(0.95) + 0.04, Y(0.08), "D", DARK);
      const off = out ? 0.22 : -0.22;
      seg(s, X(0.04), Y(0.06), X(0.80), Y(0.80), { color: RED, width: 2.2 });
      curveLabel(s, X(0.80) + 0.02, Y(0.80), "S\u2081", RED);
      seg(s, X(0.04 - off), Y(0.06 + (out ? 0.0 : 0.18)), X(0.80 - off), Y(0.80),
        { color: RED, width: 2.2, dash: "dash" });
      curveLabel(s, X(0.80 - off) + 0.02, Y(0.80) - 0.02, "S\u2082", RED);
      dot(s, X(0.48), Y(0.48), GRAY); dot(s, X(0.40), Y(0.58), RED);
      s.addText(out ? "P \u2193 , Q \u2191" : "P \u2191 , Q \u2193",
        { x: 6.3, y: 3.5, w: 3.2, h: 0.4, fontFace: FONT, fontSize: 16, bold: true,
          color: RED, margin: 0 });
    }
    if (o.side) sideNote(s, 6.3, o.side);
    if (o.caption) caption(s, o.caption);
    footer(s, n, total); if (notes) s.addNotes(notes);
    return s;
  }

  // ========================================================================
  // THEORY DIAGRAM 3 — Elasticity slopes (steep = inelastic vs flat = elastic)
  // ========================================================================
  function elasticitySlopesSlide(p, tag, title, notes, n, total) {
    const s = p.addSlide(); header(p, s, tag, title);
    // left panel: inelastic (steep)
    let ox = 0.9, oy = 4.25, pw = 3.5, ph = 2.7;
    let A = plot(s, ox, oy, pw, ph, "Q", "P");
    seg(s, A.X(0.40), A.Y(0.92), A.X(0.60), A.Y(0.06), { color: DARK, width: 2.6 });
    s.addText("Steep \u2192 INELASTIC", { x: ox, y: oy + 0.30, w: pw + 0.4, h: 0.3,
      fontFace: FONT, fontSize: 13, bold: true, color: DARK, align: "center", margin: 0 });
    s.addText("big \u0394P, small \u0394Q", { x: ox, y: oy + 0.58, w: pw + 0.4, h: 0.26,
      fontFace: FONT, fontSize: 11, italic: true, color: GRAY, align: "center", margin: 0 });
    // right panel: elastic (flat)
    ox = 5.7;
    let B = plot(s, ox, oy, pw, ph, "Q", "P");
    seg(s, B.X(0.05), B.Y(0.62), B.X(0.95), B.Y(0.38), { color: RED, width: 2.6 });
    s.addText("Flat \u2192 ELASTIC", { x: ox, y: oy + 0.30, w: pw + 0.4, h: 0.3,
      fontFace: FONT, fontSize: 13, bold: true, color: RED, align: "center", margin: 0 });
    s.addText("small \u0394P, big \u0394Q", { x: ox, y: oy + 0.58, w: pw + 0.4, h: 0.26,
      fontFace: FONT, fontSize: 11, italic: true, color: GRAY, align: "center", margin: 0 });
    footer(s, n, total); if (notes) s.addNotes(notes);
    return s;
  }

  // ========================================================================
  // THEORY DIAGRAM 4 — Supply over time (the hero fan): demand + S_im/S_sr/S_lr
  // ========================================================================
  function supplyOverTimeSlide(p, tag, title, opts, notes, n, total) {
    const o = opts || {};
    const s = p.addSlide(); header(p, s, tag, title);
    const ox = 1.1, oy = 4.35, pw = 4.9, ph = 2.85;
    const { X, Y } = plot(s, ox, oy, pw, ph, "Q", "P");
    // demand (dark)
    seg(s, X(0.05), Y(0.90), X(0.95), Y(0.12), { color: DARK, width: 2.4 });
    curveLabel(s, X(0.95) + 0.04, Y(0.12), "D", DARK);
    // three supply curves through a common low point, fanning from vertical to flat
    const baseX = 0.30, baseY = 0.06;
    // immediate: near-vertical
    seg(s, X(baseX), Y(baseY), X(baseX + 0.04), Y(0.95), { color: RED, width: 2.6 });
    curveLabel(s, X(baseX + 0.04) - 0.02, Y(0.95) + 0.02, "S\u1d62\u2098", RED);
    // short run: moderate slope
    seg(s, X(baseX), Y(baseY), X(baseX + 0.45), Y(0.95), { color: RED, width: 2.2, dash: "dash" });
    curveLabel(s, X(baseX + 0.45) + 0.02, Y(0.95), "S\u209b\u1d63", RED);
    // long run: flat
    seg(s, X(baseX), Y(baseY), X(0.98), Y(0.55), { color: RED, width: 2.0, dash: "sysDot" });
    curveLabel(s, X(0.98) + 0.02, Y(0.55), "S\u2097\u1d63", RED);
    if (o.side) sideNote(s, 6.4, o.side);
    if (o.caption) caption(s, o.caption);
    footer(s, n, total); if (notes) s.addNotes(notes);
    return s;
  }

  // ========================================================================
  // EMPIRICS — chart slide (native addChart) with source caption + data tag
  // type: "line" | "bar" ; data: pptxgenjs chart data array
  // ========================================================================
  function chartSlide(p, tag, title, type, data, opts, source, question, notes, n, total) {
    const o = opts || {};
    const s = p.addSlide(); header(p, s, tag, title);
    const chartType = (type === "bar") ? p.charts.BAR : p.charts.LINE;
    s.addChart(chartType, data, Object.assign({
      x: 0.7, y: 1.5, w: 8.6, h: 2.9,
      chartColors: o.colors || [RED, DARK, GRAY],
      showLegend: !!o.legend, legendPos: "b", legendFontFace: FONT, legendFontSize: 10,
      showTitle: false, lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 6,
      catAxisLabelFontFace: FONT, catAxisLabelFontSize: 10, catAxisLabelColor: BODY,
      valAxisLabelFontFace: FONT, valAxisLabelFontSize: 10, valAxisLabelColor: BODY,
      valGridLine: { style: "none" }, catGridLine: { style: "none" },
      valAxisTitle: o.ytitle || "", showValAxisTitle: !!o.ytitle,
      valAxisTitleFontFace: FONT, valAxisTitleFontSize: 10,
    }, o.chartOpts || {}));
    if (source) caption(s, source);
    if (question) {
      s.addShape(p.shapes.RECTANGLE, { x: 0.4, y: 4.92, w: 0.08, h: 0.30, fill: { color: RED } });
      s.addText(question, { x: 0.6, y: 4.90, w: 9.0, h: 0.34,
        fontFace: FONT, fontSize: 11.5, italic: true, color: DARK, valign: "middle", margin: 0 });
    }
    footer(s, n, total); if (notes) s.addNotes(notes);
    return s;
  }

  return { sdCrossSlide, shiftSlide, elasticitySlopesSlide, supplyOverTimeSlide, chartSlide };
};
