# The Bieri AI Ecosystem (Unified)

**Who:** David Bieri, Virginia Tech SPIA (bieri@vt.edu)
**What:** A unified architecture for AI-assisted workflows across multiple platforms (Claude, Manus, etc.)
**Where:** Managed in the `bieri-ai` monorepo on GitHub.

## Core Rules

1. **Read `{DOMAIN}_SESSION_NOTES.md`** before doing anything in a new session — on any platform.
2. **Write `{DOMAIN}_SESSION_NOTES.md`** before ending any substantive session — on any platform.
3. **Any skill change** must update `SKILLS_MANIFEST.md` in the relevant domain before the session closes.
4. **Skills MUST be written** in platform-agnostic Markdown (`skill.md`). Use adapters to generate platform-specific formats.
5. **Run the appropriate validator** after wrapping: `audit_skill.py` (Claude) or `quick_validate.py` (Manus).

## Architecture

The ecosystem uses a 3-layer pattern across 5 domains (Research, Teaching, Admin, WebDev, Home):

- **Fast** — `{PREFIX}_SESSION_NOTES.md` — in-flight state, read at start, written at end.
- **Slow** — `SKILLS_MANIFEST.md` — stable record of decisions, milestones, skills.
- **Skills** — Platform-agnostic capabilities stored in `bieri-ai/skills/`.

## Adapters

Skills are executed by different platforms, which require different metadata wrappers:

- **Claude:** `adapters/claude/wrap_skill.py` generates `.skill` files for upload to Claude Desktop.
- **Manus:** `adapters/manus/wrap_skill.py` generates `SKILL.md` with YAML frontmatter for the Manus sandbox.

## Skill Namespaces

- `(universal)` — e.g., `session-handover`, `web-release-workflow`
- `course:*` — Teaching domain
- `webdev:*` — WebDev domain
- `research:*` — Research domain
- `admin:*` — Project-specific tools
