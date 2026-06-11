# session-handover

A universal protocol for clean continuity across Claude sessions.
Applies to all of David's projects — teaching, AGW website, SPIA white
paper, dissertation advising, and any future project.

**Design principle:** The *protocol* lives here (universal). The *project
context* lives in the SESSION_NOTES file (project-specific). Adding a new
project means creating a new SESSION_NOTES with a config block — not
writing a new skill.

---

## When to invoke

### At session END — write `{PREFIX}_SESSION_NOTES.md`

Triggers (any one):
- David says "handover", "wrap up", "let's stop here", "switching chats",
  "prep next session", "compaction prep", "end of session"
- Substantive work done and items are waiting to be dispatched
- Version milestone, skill bump, or deploy reached
- Context window getting full and another sub-task is starting

### At session START — read `{PREFIX}_SESSION_NOTES.md`

Triggers (any one):
- A new chat opens on any project David works on
- David refers to something "we did" or "we decided" with no current context
- David asks about status of anything in-flight

**Read the SESSION_NOTES file from Project knowledge BEFORE writing any
code, producing any files, or asking what David needs.** Find the file by
searching Project knowledge for `SESSION_NOTES`. If multiple files exist,
ask which project David wants to continue. If no file exists, ask David
where to start and offer to create the SESSION_NOTES template.

---

## Project configuration block

Every `{PREFIX}_SESSION_NOTES.md` opens with this block, which tells the
skill everything that differs across projects. Fill it in when creating a
new project's session notes for the first time.

```markdown
## Project configuration
**Prefix:** [e.g. TEACHING, AGW, SPIA, JANE]
**Registry:** [slow-moving authoritative file, e.g. SKILLS_MANIFEST.md]
**Dispatch:**
  → [target 1] ([what goes there])
  → [target 2] ([what goes there])
**Horizon:** [next hard deadline]
```

### Reference: known projects

**Teaching** (`TEACHING_SESSION_NOTES.md`):
```
**Prefix:** TEACHING
**Registry:** SKILLS_MANIFEST.md (in Project knowledge)
**Dispatch:**
  → Claude Customize   (.skill files — install via Cowork → Customize → Skills)
  → Project knowledge  (KB, manifest, session notes)
  → OneDrive/Teaching/ (source files, scripts, decks)
  → Canvas             (student-facing content)
**Horizon:** [semester start / recording deadline / sabbatical]
```

**AGW website** (`AGW_SESSION_NOTES.md`):
```
**Prefix:** AGW
**Registry:** AGW_PROGRESS.md + AGW_DECISIONS.md
**Dispatch:**
  → git push           (git add <files> && git commit -m "..." && git push)
**Horizon:** [conference date / T-minus days]
```

---

## The handover document — six sections

Use this exact structure in `{PREFIX}_SESSION_NOTES.md`:

```markdown
# {PREFIX} Session Notes

**Last session:** YYYY-MM-DD
**Topic:** one-line summary of what this session was about
**[Horizon label]:** [next hard deadline]

---
[Project configuration block — see above]
---

## 1. Completed this session

Work done and confirmed dispatched. Use ✓ for confirmed, ? for
"produced but dispatch unconfirmed".

- ✓ `filename` → [target] — one-line description
- ? `filename` → [target] — one-line description

## 2. Pending dispatch

Items produced but not yet sent to their target. This is the
most-used section — be precise.

**[Target name]**
- `filename` — rationale

For git-deploy projects, include the exact commit block:
  git add <files>
  git commit -m "<message>"
  git push

For skill installs, include the navigation path:
  Claude Desktop → Cowork → Customize → Skills → + → upload

## 3. Decisions made this session

Conventions, architectural choices, or scope decisions that should
be remembered. Bold the decision; follow with one-line rationale.

If a decision changes a registry file, note whether that update
was made.

Also capture here: **any skill candidates identified but not built**.
Add them to the manifest's `## Candidate skills` section with a trigger
condition — don't leave them only in the session notes.

## 4. Latent issues surfaced

Bugs, gaps, or inconsistencies noticed but NOT fixed this session.
Full path and location when known.

## 5. Open questions

Items waiting on David's input — content, design, scope, scheduling.

## 6. Suggested next session

One concrete starting point. Write it as the opening message of the
next chat:
  "Read {PREFIX}_SESSION_NOTES.md, then [specific action]."
```

---

## Writing rules

- **Name the dispatch target.** Every pending item must say where it goes.
- **Be honest about uncertainty.** Use `?` for unconfirmed dispatches.
- **Record conventions, not just files.** If a session established that
  descriptions must be ≤200 chars or that n/N footer fractions are standard,
  that belongs in section 3.
- **Don't duplicate the registry.** Once something is in SKILLS_MANIFEST.md
  or AGW_PROGRESS.md, session notes just reference it by version or ID.
- **Brevity is a feature.** Session notes fit in 1–2 screens. Longer content
  migrates to the slow-moving registry files.
- **Keep the horizon visible.** State the next hard deadline every session.

---

## Promotion rules

| From | Moves to | When |
|------|----------|------|
| Pending dispatch (§2) | Completed (§1) | Next session, after confirmed dispatch |
| Completed (§1) | Registry file | At next version/milestone |
| Open question (§5) | Decision (§3) or pending dispatch (§2) | When answered |
| Latent issue (§4) | Completed (§1) | When fixed |
| Latent issue (§4) | Registry blocker table | When it becomes a hard blocker |

---

## Anti-patterns

Don't write a handover that:
- Lists everything discussed (conversation history covers that)
- Omits dispatch targets from pending items
- Buries blockers in narrative prose instead of §4 or §5
- Is missing the horizon / next deadline
- Exceeds 2 screens (migrate stable content to the registry)
- Restates decisions already in the registry file

---

## File family (per project)

Each project has a slow-moving layer and a fast-moving layer:

| Layer | Teaching | AGW website |
|-------|---------|-------------|
| Slow — what is | `SKILLS_MANIFEST.md` | `AGW_PROGRESS.md` |
| Slow — why decided | *(in manifest notes)* | `AGW_DECISIONS.md` |
| Slow — orientation | KB, syllabi | `AGW_README.md`, `AGW_CLAUDE.md` |
| **Fast — in-flight** | **`TEACHING_SESSION_NOTES.md`** | **`AGW_SESSION_NOTES.md`** |

For a new project, create the fast-moving file first (with the config
block) and add the slow-moving registry as the project grows.

---

## Architecture reference

This skill operates within a four-domain, three-layer architecture. Read
`BIERI_CLAUDE.md` from Project knowledge for the full reference.

| Domain | Session notes (fast) | Registry (slow) | Skills |
|--------|---------------------|----------------|--------|
| Research | `RESEARCH_SESSION_NOTES.md` | progress log | — |
| Teaching | `TEACHING_SESSION_NOTES.md` | `SKILLS_MANIFEST.md` | `teaching:*` (7 active) |
| Admin | `{PROJECT}_SESSION_NOTES.md` | project progress + decisions | (project-specific) |
| Home | `HOME_SESSION_NOTES.md` | registry | — |

**Three layers per domain:**
- **Fast** — `{PREFIX}_SESSION_NOTES.md`: in-flight state, updated every session
- **Slow** — registry file(s): stable, authoritative, rarely changed
- **Skills** — domain-specific Claude skills (`teaching:*` namespace for Teaching)

**Meta layer:** `teaching:skill-builder` + `audit_skill.py` governs the skills library.

**Starting a new domain:** create `{PREFIX}_SESSION_NOTES.md` with the project
configuration block (see "Project configuration block" section above) and add
it to the Project knowledge. The registry and skills layers grow as the domain
matures. No new skill required — this skill handles any domain automatically.

**Architecture diagram:** `BIERI_CLAUDE_ARCHITECTURE.svg` and `.html`
stored at `OneDrive/Teaching/Architecture/`.


---

## Version history

- **1.1.0** (2026-06-09): Added Architecture reference section with
  four-domain table, layer descriptions, and diagram pointer.
- **1.0.0** (2026-06-09): Created by consolidating `agw-handover`
  (AGW website project) and `teaching:handover` (teaching project) into a
  single generic skill. Both predecessors retired.
