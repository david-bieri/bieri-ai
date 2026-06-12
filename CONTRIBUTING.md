# Contributing to bieri-ai

This document outlines the governance rules, update ceremonies, and lifecycle management for the `bieri-ai` ecosystem.

> **Quick reference for agents:** [`AGENTS.md`](AGENTS.md) is the short, pasteable version of the skill contract (the six invariants), auto-discovered by repo-reading tools and safe to paste into a Manus task or Perplexity prompt. This document is the full ruleset behind it. The auditor (`audit_skill.py --all`) enforces the contract in CI on every push and PR.

## 1. The Golden Rule of State

**No AI session may end with uncommitted state.**

Before you close a Claude chat window or terminate a Manus task:
1. Update `{DOMAIN}_SESSION_NOTES.md` with what was accomplished.
2. If any skills were created or modified, update `SKILLS_MANIFEST.md` in the relevant domain.
3. Commit and push changes to the `bieri-ai` repository.

## 2. Skill Lifecycle

Skills are living documents. They evolve through use.

### Creating a New Skill
1. Identify a repeatable pattern during a session.
2. Run `./tools/new-project.sh` or copy `templates/skill_template.md` to create the scaffold.
3. Draft the skill in platform-agnostic Markdown.
4. Add the skill to the relevant domain's `SKILLS_MANIFEST.md` under "Installed Skills".
5. Run the wrapper (`adapters/claude/wrap_skill.py` or `adapters/manus/wrap_skill.py`) to generate the deployable artifact.

### Updating an Existing Skill
1. Edit the `skill.md` file directly.
2. If the skill behavior changes significantly, update the `version` and `updated` date in the `metadata.yaml` sidecar (if it exists) or note the change in the commit message.
3. Run the wrapper to regenerate the deployable artifact.
4. Log the update in the `SKILLS_MANIFEST.md` Update Log table.

### Deprecating a Skill
1. Move the skill directory to `archive/skills/`.
2. Remove it from the "Installed Skills" table in `SKILLS_MANIFEST.md`.
3. Add an entry to the Update Log noting the deprecation and reason.

## 3. Writing Platform-Agnostic Skills

The core innovation of `bieri-ai` is that knowledge is separated from execution. To maintain this:

- **DO NOT** include YAML frontmatter in `skill.md`. The adapters handle this.
- **DO NOT** hardcode platform-specific instructions (e.g., "Upload this to Claude Projects" or "Run this in the Manus sandbox"). Instead, describe the *capability* and the *trigger*.
- **DO** use clear Markdown headings, especially `## When to invoke` and `## Instructions`.
- **DO** bundle necessary scripts or references in `scripts/` or `references/` subdirectories within the skill folder.

## 4. Manifest Governance

Each domain (`research`, `teaching`, `admin`, `webdev`) maintains a `SKILLS_MANIFEST.md`. This is the "slow layer" of the architecture.

- The manifest is the single source of truth for what skills are currently active in that domain.
- The "Candidate Skills" table should be used to capture ideas for skills that emerge during sessions but aren't yet built.
- The "Update Log" at the bottom of the manifest must be appended whenever the skill roster changes.

## 5. Adapter Maintenance

If Anthropic or Manus changes their required skill formats:
1. Update the relevant `wrap_skill.py` script in `adapters/`.
2. For Claude, update `audit_skill.py` to reflect the new compliance rules.
3. Re-run the wrapper on all skills to regenerate the artifacts. No `skill.md` files should need to change.
