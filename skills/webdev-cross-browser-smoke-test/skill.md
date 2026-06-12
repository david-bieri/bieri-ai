# webdev:cross-browser-smoke-test

This skill defines a rigorous methodology for testing static sites and interactive web applications before merging branches.

## When to invoke

Trigger on: "smoke test the site", "test before merging", "QA this branch", "check it works across browsers", "verify the build before release", or any pre-merge verification of a static site or web app. Invoked by `webdev:release-workflow` at Step 1.

---

## The Testing Methodology

When asked to perform a "smoke test," systematically verify the application across several dimensions using browser tools to navigate, click, and inspect the DOM/Console.

### 1. The Checklist

A typical SPA/Dashboard checklist:

1. **Initial Load & Routing**: Does the landing page load? Do navigation links work?
2. **Core Modules (Tab by Tab)**: Open every major view/tab. Ensure the primary visualization renders.
3. **Interactivity**: Test dropdowns, hover tooltips, click events (e.g., detail panels, filters).
4. **Forms & Inputs**: Test search bars, filtering, language toggles.
5. **Responsiveness**: Verify mobile layout behavior via CSS inspection.
6. **Console Health**: Check for silent JS errors.

### 2. Console Verification

Always check the browser console after loading complex modules:

```javascript
// Using browser_console_exec — check for errors
window.__errors = []; window.addEventListener('error', e => __errors.push(e.message));
// Later: return window.__errors;
```

### 3. Responsive Layout Testing

Inspect CSS rules governing mobile layout rather than resizing the viewport:

```javascript
const tabs = document.querySelector('.sub-tabs');
const style = window.getComputedStyle(tabs);
return { overflowX: style.overflowX, flexWrap: style.flexWrap };
```

Look for `overflow-x: auto` and `flex-wrap: nowrap` on horizontal scrolling elements.

### 4. Interactive Element Verification

For D3/SVG visualizations, hover over elements to trigger tooltips:
- Use `browser_console_exec` to find the exact viewport coordinates of an SVG element.
- Use `browser_move_mouse` to hover over those coordinates.

## The Smoke Test Report

While testing, continuously append results to `smoke_test_report.md`. Deliver this report to the user upon completion.

**Template:**

```markdown
# Smoke Test Report: `branch-name`

**Date:** YYYY-MM-DD
**Status:** PASS / FAIL

## 1. Landing & Navigation
- [x] Initial load successful
- [x] Header/Footer links resolve correctly

## 2. Core Modules
- [x] Module A: Renders correctly, interactions work.
- [x] Module B: Data displays, tooltips fire.

## 3. Responsiveness & UI
- [x] Mobile sub-tabs scroll horizontally.
- [x] i18n toggle works both directions.

## 4. Console Health
- [x] Zero unhandled exceptions.

## Conclusion
The branch is stable and ready for merge.
```

## Related Skills

| After smoke test passes | Skill |
|------------------------|-------|
| Proceed with the full release | `web-release-workflow` (Step 1 complete, continue to Step 2) |
