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
1. Copy `templates/skill_template.md` to `skills/<namespace>-<name>/skill.md` (directory hyphenated; H1 colon-namespaced).
2. Write the skill logic in platform-agnostic Markdown — **no YAML frontmatter** (the adapter adds it).
3. Copy `templates/metadata.yaml` alongside it and fill in `description` (≤200 chars), `version`, and `depends_on`/`used_by`. `name` is derived from the directory — never set it here.
4. Register the skill in the relevant domain's `SKILLS_MANIFEST.md`.
5. Run the appropriate adapter in `adapters/` to generate the platform-specific format.

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

Identity is colon-namespaced; the directory is the hyphenated equivalent (`teaching:news-hooks` lives in `skills/teaching-news-hooks/`). Each skill is a platform-agnostic `skill.md` plus a `metadata.yaml` sidecar (authored description, version, `depends_on`/`used_by`).

### Universal
| Skill | Purpose |
|-------|---------|
| `session-handover` | Session state continuity across all domains |

### Admin (`admin:*`)
| Skill | Purpose |
|-------|---------|
| `admin:cron-agent` | Durable recurring agent cron jobs (single-invocation pattern) |
| `admin:gmail-scanner` | Gmail intake → structured calendar items → app API |
| `admin:tag-parser` | `#TAG @Name` subject-line classification |
| `admin:family-hub` | Full-stack family administration app (orchestrates the above) |

### Teaching (`teaching:*`)
| Skill | Purpose | Bundled Resources |
|-------|---------|-------------------|
| `teaching:news-hooks` | "In the news" slide search and formatting | — |
| `teaching:build-kb` | PPTX → KB extraction | `scripts/build_kb.py` |
| `teaching:video-scripts` | Narration scripts at 130 wpm | — |
| `teaching:compose-slides` | Lecture decks in house style | `references/house-style.md`, `references/slide-library.md` |
| `teaching:assess-from-kb` | Assessment generation from KB | — |
| `teaching:skill-builder` | Skill library creation and maintenance | `scripts/audit_skill.py` |

### WebDev (`webdev:*`)
| Skill | Purpose |
|-------|---------|
| `webdev:vite-express` | Vite + Express full-stack scaffold and build pipeline |
| `webdev:supabase-app` | Supabase schema, RLS, migrations, real-time |
| `webdev:deploy-render` | Deploy apps + cron to Render.com |
| `webdev:platform-migration` | Sandbox → self-hosted portability migration |
| `webdev:release-workflow` | Orchestrator for merge/deploy ceremonies |
| `webdev:static-site-i18n` | Multi-page static site + client-side i18n |
| `webdev:d3-analytics-modules` | D3/React analytics dashboards |
| `webdev:json-data-enrichment` | JSON dataset transformation |
| `webdev:latex-pdf-guide` | LaTeX guide compilation + web delivery |
| `webdev:cross-browser-smoke-test` | Pre-merge QA smoke testing |
| `webdev:contact-protocol-links` | Zero-infrastructure contact channels |
| `webdev:messaging-inapp-sms` | In-app + inbound-SMS messaging *(source reconstruction pending)* |
| `webdev:node-build-pitfalls` | CI build pitfalls reference *(source reconstruction pending)* |

### Research (`research:*`) / Home (`home:*`)
No skills yet — greenfield. `home:` is reserved; household skills currently live in `admin:*`.
