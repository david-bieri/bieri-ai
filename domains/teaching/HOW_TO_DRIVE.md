# How to Drive the Teaching Skills

A practical reference for invoking the `teaching-*` skill suite. You drive by
**describing the task in plain language** — Claude reads the installed skill
descriptions and loads the right one(s), often several at once. You rarely name a
skill; you can pin one when you want to force the route.

> Lives at `domains/teaching/`. Companion to `SKILLS_MANIFEST.md` (the registry) and
> `TEACHING_SESSION_NOTES.md` (current state).

## The suite at a glance

| You want… | Say something like… | Skill(s) |
|---|---|---|
| A lecture/video deck in house style | "Build the Week 3 Real Estate Law videos [L3.x] for SU26" | teaching-compose-slides |
| A theory diagram | "Make a demand-shift diagram for Beamer" / "supply-fan as a vector PDF" | teaching-diagrams |
| A data chart | "Chart mortgage rates + housing starts since 2015 from FRED, house style" | teaching-charts |
| A current-events opener | "Find a commercial-vacancy story and make an 'In the news' slide" | teaching-news-hooks |
| Narration for async video | "Write 130-wpm speaking notes for this deck, ~11 min" | teaching-video-scripts |
| Quiz/exam/discussion items | "From the KB, draft a 10-question Week 2 quiz with a key" | teaching-assess-from-kb |
| Refresh the course KB | "Rebuild the KB from the SU26 + S24 decks" | teaching-build-kb |
| An AER table for a paper | "Make a booktabs table from these results, SEs in parens, with a caption" | teaching-charts (`latex_table`) |
| Restore/close context | "Read the session notes and continue" / "write session notes" | session-handover |
| A new or revised skill | "Add a box-whisker variant that marks the mean" | teaching-skill-builder |

## Chained workflows (the real payoff)

One prompt can run a whole production line.

- **Spin up a unit** → build-kb → compose-slides + news-hooks + diagrams + charts +
  video-scripts. *"Rebuild the KB, then build the three Week 3 videos: news-hook opener,
  a diagram where a concept needs one, 130-wpm narration."*
- **One figure, two homes** → diagrams + charts produce vector PDF (paper/Beamer) and
  PNG (deck) from one source, captioned once via `captions.yaml`.
- **Assessment that matches what you taught** → assess-from-kb stays grounded in the KB.
- **Cross-context reuse** → same engine, `setCourse()` for a different footer, PPTX
  instead of Beamer when a host needs to edit (guest lectures, UAP 4714, VLLI).

## How invocation works

- **Describe tasks, not skills** — pin one ("use teaching-charts") only to force it.
- **Build-heavy skills need an execution environment** (filesystem + `make`): run
  compose-slides, diagrams, charts, and build-kb in **Claude Cowork or Claude Code**.
  Lighter draft work (a news hook, an outline, quiz items) is fine in plain chat.
- **KB + session notes are the context backbone.** Open a session with "read the session
  notes"; the KB keeps decks and quizzes course-accurate instead of generic.
- **Tag grammar** stays consistent: `· <concept>` (theory diagram) · `· In the data …`
  (empirical chart) · `· In the (macro-)news …` (news hook).
- **Rebuild figures** anytime with `make -C tools all` → `build/figures/`.

## Example kickoff prompts

**Next unit (Week 3):** see the block in `TEACHING_SESSION_NOTES.md` §6.

**A single figure:**
> "Make a supply-over-time fan diagram and a FRED chart of housing starts since 2015 —
> vector PDFs with AER captions for the paper, and PNGs for the lecture deck."

**A quiz:**
> "From the KB, draft a Week 2 quiz on supply/demand, equilibrium, and elasticity —
> 8 MCQs plus 2 discussion prompts, with an answer key."

**A guest deck:**
> "Build a host-editable PowerPoint on fiscal federalism for ECON 4135 — house style,
> one system diagram, one FRED inflation chart."
