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
