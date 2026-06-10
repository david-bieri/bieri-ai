# bieri-ai

Unified AI workflow infrastructure for David Bieri (bieri@vt.edu).

This monorepo consolidates the architecture previously split across `bieri-claude`, `bieri-teaching`, `bieri-research`, `bieri-admin`, and `bieri-manus`. It provides a single source of truth for all AI-assisted workflows across all execution platforms (Claude, Manus, etc.).

---

## The Architecture

See `architecture/BIERI_AI_ARCHITECTURE.html` for the visual architecture diagram, or read the full design document in `architecture/BIERI_AI.md`.

**Key Principle:** Skills are platform-agnostic knowledge. They are written once in Markdown (`skill.md`) and wrapped by platform-specific adapters before deployment.

---

## Directory Structure

| Path | Purpose |
|------|---------|
| `architecture/` | Design documents and diagrams defining the ecosystem |
| `domains/` | Session state, registries, and progress logs (fast/slow layers) |
| `skills/` | Platform-agnostic skill definitions (the knowledge base) |
| `adapters/` | Scripts to wrap `skill.md` into `.skill` (Claude) or `SKILL.md` (Manus) |
| `templates/` | Scaffolding for new projects and skills |
| `tools/` | Universal utilities like `new-project.sh` |

---

## Domains

Work is divided into five pillars:

1. **Research** — `domains/research/` (Claude)
2. **Teaching** — `domains/teaching/` (Claude)
3. **Admin** — `domains/admin/` (Claude + Manus)
4. **WebDev** — `domains/webdev/` (Manus)
5. **Home** — `domains/home/` (Claude)

Each domain contains a `SKILLS_MANIFEST.md` registry and session notes.

---

## Getting Started

### Start a new project
```bash
./tools/new-project.sh <pillar> <prefix> "<Project name>"
```
Example: `./tools/new-project.sh webdev AGW "AGW Conference Site"`

### Add a new skill
1. Copy `templates/skill_template.md` to `skills/<namespace>-<name>/skill.md`
2. Write the skill logic in platform-agnostic Markdown.
3. Use the appropriate adapter in `adapters/` to generate the platform-specific format.

### Package skills for deployment
```bash
# For Claude (produces .skill ZIP)
python adapters/claude/wrap_skill.py skills/<name>

# For Manus (produces SKILL.md directory)
python adapters/manus/wrap_skill.py skills/<name>

# Wrap all skills at once (Manus)
python adapters/manus/wrap_skill.py --all
```

---

## Core Workflows

For full governance rules, see [CONTRIBUTING.md](CONTRIBUTING.md).

### 1. The Session Handover
Whenever you start or end an AI session (Claude chat or Manus task):
1. **Start:** Upload or attach the relevant domain's `{PREFIX}_SESSION_NOTES.md`. Ask the AI to read it to restore context.
2. **End:** Ask the AI to summarize the session's accomplishments and update `{PREFIX}_SESSION_NOTES.md`.
3. **Commit:** Push the updated notes to GitHub before closing the window.

### 2. The Skill Creation Loop
When you notice a repeatable pattern:
1. Run `./tools/new-project.sh` or copy `templates/skill_template.md` to create `skills/<name>/skill.md`.
2. Write the skill instructions in platform-agnostic Markdown.
3. Update the `SKILLS_MANIFEST.md` in the relevant domain.
4. Run the appropriate adapter (see "Package skills for deployment" above).
5. Commit and push.

### 3. The Deployment Loop
- **Claude:** Upload the generated `.skill` ZIP file to Claude Desktop (Cowork → Customize → Skills → + → upload).
- **Manus:** Attach the `bieri-ai` GitHub repository to your Manus task. Manus will automatically discover the wrapped skills in `dist/manus/` (if committed) or you can instruct Manus to run the wrapper script itself.

---

## Skills Inventory

### Universal
| Skill | Purpose |
|-------|--------|
| `session-handover` | Session state management across all domains |
| `web-release-workflow` | Orchestrator for merge/deploy ceremonies |

### Teaching (`teaching-*`)
| Skill | Purpose | Bundled Resources |
|-------|---------|-------------------|
| `teaching-news-hooks` | "In the news" slide search and formatting | — |
| `teaching-build-kb` | PPTX → KB extraction | `scripts/build_kb.py` |
| `teaching-video-scripts` | Narration scripts at 130 wpm | — |
| `teaching-compose-slides` | Lecture decks in house style | `references/house-style.md`, `references/slide-library.md` |
| `teaching-assess-from-kb` | Assessment generation from KB | — |
| `teaching-skill-builder` | Skill library creation and maintenance | `scripts/audit_skill.py` |

### WebDev (`webdev-*`)
| Skill | Purpose |
|-------|--------|
| `webdev-static-site-i18n` | Multilingual static site management |
| `webdev-d3-analytics-modules` | D3/React analytics dashboards |
| `webdev-json-data-enrichment` | JSON dataset transformation |
| `webdev-latex-pdf-guide` | LaTeX user guide compilation |
| `webdev-cross-browser-smoke-test` | Structured QA testing |
| `webdev-contact-protocol-links` | Zero-infrastructure contact channels |
