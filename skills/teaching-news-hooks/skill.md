
# teaching:news-hooks

## When to invoke

Trigger on any of these: building or updating a lecture deck that needs news hooks;
"add a news hook"; "find a current story about X"; "In the news slide for module N";
"current events for week/lecture"; "connect [concept] to something in the news".
Always use this skill — do not improvise the format from memory.

---

Generates "In the news" slides in Prof. Bieri's exact format: image-forward layout,
correct tag variant, URL caption, and a single focused discussion question.

---

## Tag variant taxonomy

Choose the tag based on the story's scope:

| Tag | Use when the story is about… |
|-----|------------------------------|
| `In the (micro-)news …` | A specific property, transaction, firm, city, or market segment |
| `In the (macro-)news …` | Broad economic conditions, national/global trends, interest rates, trade policy |
| `In the (policy-)news …` | Zoning, land use regulation, tax policy, housing vouchers, rent control |
| `In the (environmental-)news …` | Climate risk, insurance withdrawal, contamination, green building, sustainability |

---

## Preferred sources (search these first)

- **The Wall Street Journal** — real estate section
- **The Economist** — property section
- **HousingWire** — residential markets, mortgage, lending
- **ULI Magazine / Urban Land** — development, investment, ESG, resilience
- **GlobeSt** — commercial real estate
- **CoStar News** — market data, CRE transactions
- **FRED (Federal Reserve Economic Data)** — data hooks (vacancy rates, starts, mortgage rates)
- **Seeking Alpha** — REIT analysis and investor commentary
- **NYT Real Estate section**

Search for stories published in the **last 6–12 months**. Prefer stories with
specific quantitative claims (rates, percentages, dollar figures) that students
can verify and discuss.

---

## Placement rules

Each deck typically carries **two** news hooks:

1. **Opening hook (slide 2)** — motivates the lecture. Poses a puzzle or current
   example that the lecture's framework will help explain. Framed as: *here's a
   real-world problem; by the end of this video you'll be able to read stories like
   this analytically.*

2. **Closing hook (penultimate slide, before recap)** — synthesizes. Shows the
   lecture concepts in action. Framed as: *here's that same story, now you have the
   tools to read it.*

For a single standalone hook, default to the closing/synthesis position.

---

## Workflow

### Step 1 — Identify the concept and lecture code

Extract from context:
- The **lecture code** (e.g., `[L2.3]`, `[W2]`, `[L9.1]`) — use whatever code the
  current deck is using
- The **core concept** to hook (e.g., "market cycles", "economic base multiplier",
  "climate risk as an environmental attribute")
- Whether opening hook, closing hook, or both are needed

### Step 2 — Search for stories

Use `web_search` with 2–3 targeted queries. Example patterns:
- `"{concept}" real estate 2025 2026 WSJ HousingWire`
- `"{concept}" commercial residential housing market 2026`
- `FRED "{data concept}" current`

Fetch the most promising result with `web_fetch` to get specific figures. You need:
- Source name and date
- URL
- A specific quantitative claim or headline figure
- A connection to the lecture concept

### Step 3 — Write the slide content

Produce a `newsSlide()` call (or equivalent description) with these fields:

```
tag:       "[Lx.x] · In the (TYPE-)news …"
title:     Article headline or a punchy restatement (≤10 words)
source:    "Publication / Author (Month Year)"
url:       Full URL
question:  Single italicised discussion question connecting story to lecture concept
           — this is what students see on the slide alongside the screenshot
notes:     ~100-word narration note: briefly frame the story, state the key figure,
           connect it explicitly to the concept just covered
```

**The discussion question** is the most important element. It should:
- Be answerable using the lecture's framework
- Not be answerable by just reading the headline
- Be genuinely open-ended (no single correct answer)

Good: *"If the EBM for this region is 2.8, how many total jobs does a 500-job plant
closure imply — and what does that mean for housing demand?"*

Weak: *"What happened to office vacancy rates?"*

### Step 4 — QA

Verify:
- [ ] Tag variant is correctly chosen for the story's scope
- [ ] URL is a real, reachable article (not hallucinated)
- [ ] Quantitative claim in the notes matches the source
- [ ] Discussion question requires the lecture framework to answer
- [ ] Notes are ~100 words (narration pace)

---

## Output formats

**If building a full deck** — return pptxgenjs `newsSlide()` calls ready to paste
into the build script.

**If describing a slide** — return a structured block:

```
[TAG]
TITLE: …
SOURCE: …
URL: …
SCREENSHOT: [ Paste article screenshot here ]
DISCUSSION QUESTION: …
NARRATION NOTE: …
```

---

## Example (complete output)

**Input:** "I need a closing news hook for L2.3 (Market Analysis), specifically the
office market and buyer/seller cycles."

**Output:**

```javascript
newsSlide(p, "[L2.3] · In the (micro-)news …",
  "Office market 2026: a tale of two cities",
  "The Real Deal / CommercialCafe (May–June 2026)",
  "https://therealdeal.com/data/national/2026/u-s-office-vacancy-rates-fall/",
  "National vacancy 17.8% — down 210 bps YoY. But Austin/Dallas >20%; Miami 12.5%. " +
  "Which phase of the cycle is each city in — and what's driving the divergence?",
  "Narration: The national office vacancy rate fell to 17.8 percent in March 2026 — " +
  "a 210 basis-point improvement year-on-year. But the market-cycle framework makes " +
  "you ask: recovery where? Austin and Dallas sit above twenty percent — still a " +
  "buyer's market for tenants. Miami has dropped to twelve and a half, driven by " +
  "JPMorgan, Amazon, and Citadel relocations — a seller's market. The seller's / " +
  "buyer's / neutral framework from this video is running live, right now.",
  slideNum, totalSlides);
```
