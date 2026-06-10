
# course:assess-from-kb

## When to invoke

Trigger on: "quiz questions"; "exam questions"; "MCQs about [topic]";
"Blended Teaching questions"; "discussion prompt for week N";
"questions on module X"; "convert this lecture to assessment items".
Requires the KB in Project knowledge — search it before writing any questions.

---

Generates course-aligned assessment items grounded in Prof. Bieri's actual
slide content via the KB in Project knowledge.

---

## Prerequisites

The course KB (`REALUAP2004_KB.md`) must be uploaded to this Project's knowledge
panel. If `project_knowledge_search` returns no results for a known course concept,
the KB is not indexed — remind the user to upload it before proceeding.

---

## Question types and use cases

| Type | Platform | Bloom level | Best for |
|------|----------|-------------|---------|
| MCQ (4-option) | Blended Teaching / Canvas | Remember, Understand, Apply | Quizzes, module checks |
| Short answer | Canvas, exam | Understand, Apply, Analyze | Assignments, exam questions |
| Worked example | Canvas, exam | Apply, Analyze | Quantitative concepts (TVM, EBM, LQ) |
| Discussion prompt | Canvas Discussions, Friday sessions | Analyze, Evaluate | Weekly discussions, current-events hooks |

Default mix for a module quiz: **5 MCQ + 1 short answer**.
Default for a weekly discussion: **1 discussion prompt**.

---

## Workflow

### Step 1 — Locate content in KB

```python
project_knowledge_search("concept or topic name")
# e.g. "economic base multiplier", "bundle of rights", "market cycles seller buyer"
```

Search **2–3 times** with different phrasings to get comprehensive coverage.
Note the `[Lx.x]` slide tags in results — these anchor the questions to specific
lectures and distinguish S24 vs S26 content.

### Step 2 — Identify the concept precisely

From the KB results, extract:
- The exact definition or formula used in the course (prefer S26 formulation)
- Key distinctions the course draws (e.g., value ≠ price ≠ cost)
- Worked-example numbers already in the slides (reuse or vary these)
- The vintage: note if S24 and S26 treat the concept differently

### Step 3 — Draft questions

**For each MCQ:**
1. Write the stem (scenario > completion > question format, in that preference order)
2. Write the correct answer
3. Write 3 plausible distractors — see distractor guidance below
4. Identify the Bloom level
5. Cite the source slide tag

**For short-answer / worked example:**
1. Set up the scenario with named values
2. State the question clearly
3. Provide a model answer with units and working shown
4. Note acceptable answer range if numerical

**For discussion prompts:**
1. Reference a current-events hook if available (see `course:news-hooks`)
2. Connect the news to a course concept
3. Require the student to apply the framework, not just recall it

### Step 4 — QA against KB

For every question, verify:
- [ ] Correct answer is unambiguously supported by KB content
- [ ] No distractor is defensibly correct
- [ ] Numbers in worked examples match the KB (or are clearly stated as variations)
- [ ] Bloom level is correctly identified
- [ ] S24 vs S26 content distinction is respected (don't mix vintages in a S26 quiz)

---

## MCQ format for Blended Teaching

```
Question: [stem — one sentence or short scenario]

A) [correct answer or a distractor]
B) [distractor]
C) [distractor]
D) [distractor]

Correct: [letter]
Explanation: [1–2 sentences explaining why the correct answer is right
              and why the most tempting distractor is wrong]
Bloom level: [Remember / Understand / Apply / Analyze]
Source: [KB slide tag, e.g. [L2.1] · Market value (USPAP)]
```

Rotate the correct answer position across a question set (don't always use A).

---

## Distractor construction

Good distractors are **plausible to a student who partially understands** the concept.

| Strategy | Example concept | Good distractor |
|----------|----------------|-----------------|
| Adjacent concept confusion | Market value vs. assessed value | "The tax-assessed value" |
| Formula inversion | LQ = regional share / national share | "National share / regional share" |
| Off-by-one step | EBM chain: jobs → households → residents | Skips households, goes straight to residents |
| Real-world anchor | Disposition value | "The price achieved in a normal market sale" |
| True-but-wrong | Bundle of rights | "Ownership of the physical land only" |

**Avoid:**
- Distractors that are obviously absurd
- "All of the above" / "None of the above"
- Trick questions based on wording rather than concept

---

## Worked-example problems

For quantitative modules (TVM, EBM, appraisal), vary the numbers from KB examples
to prevent memorisation:

```
KB example:    LQ = (8,000 / 150,000) ÷ (1,500,000 / 92,000,000) = 3.27
Quiz variant:  LQ = (5,200 / 120,000) ÷ (1,800,000 / 95,000,000) = ?
               [Answer: (0.0433) / (0.01895) ≈ 2.29 → basic industry]
```

Always verify your own arithmetic. State the answer with units and the
interpretation ("LQ > 1, so this industry is basic").

---

## Discussion prompt format

```
Context: [1-sentence current event or scenario]
Connection: [the course concept it illustrates]
Prompt: [open question requiring the framework to answer — not answerable by
         just recalling a definition]

Example:
Context: Farmers Insurance has exited large parts of the Florida homeowners
         insurance market, with premiums rising 38% since 2024 in Louisiana.
Connection: Environmental attributes and their effect on property value
Prompt: Using the five-attribute framework, explain how the insurance withdrawal
        functions as an environmental attribute and trace its likely effect on
        property values in affected coastal markets. Which other attributes might
        be simultaneously affected, and why?
```

---

## Module-level coverage notes (REAL/UAP 2004, S26)

| Module | High-yield assessment areas |
|--------|-----------------------------|
| 2 | Value vs. price vs. cost; four value types; USPAP fair market value definition |
| 2 | Five attributes; bundle of rights; public vs. private limitations |
| 2 | EBM chain; LQ calculation; basic vs. non-basic employment |
| 3 | Supply/demand mechanics; market cycles; two-market system |
| 4 | Bundle of rights; zoning; deed restrictions; easements |
| 5 | TVM; PV/FV; DCF; annuities |
| 6 | Three appraisal approaches; highest and best use |
| 7 | Rent vs. own analysis; affordability; user-cost formula |
| 8 | Mortgage mechanics; amortisation; ARM vs. fixed |
| 9 | Commercial leases; NOI; cap rate; basic DCF |
| 10 | REIT structure; equity vs. mortgage REITs; dividend yields |
| 12 | Development feasibility; irreversibility; real options |
| 13 | Public policy; housing vouchers; zoning reform |

---

## Vintage-aware generation

When the KB contains both S24 and S26 content for the same module number:
- Default to **S26 formulations** for current-semester quizzes
- If asked for S24 content specifically, note it as `[S24]` in the source citation
- Do not mix S24 and S26 definitions in the same question set — pick one vintage
