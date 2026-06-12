# AGENTS.md — bieri-ai skill contract

**Any agent — Claude, Codex, Manus, Perplexity, or otherwise — that creates or edits a skill in this repo MUST follow the invariants below.** Full rules live in `CONTRIBUTING.md`; this is the short, pasteable version. CI runs the auditor on every push and PR, so non-compliant skills fail the build.

## The six invariants

1. **Directory is hyphenated; identity is colon.** A skill lives in `skills/<namespace>-<name>/`, and its `skill.md` H1 is `# <namespace>:<name>` (dir `teaching-news-hooks` → H1 `# teaching:news-hooks`). Namespaces: `admin`, `teaching`, `research`, `webdev`, `home`. Universal skills (e.g. `session-handover`) are **bare** — no prefix, H1 is just `# session-handover`.

2. **No frontmatter in `skill.md`.** The source is pure Markdown starting at the H1. The adapter adds frontmatter at wrap time.

3. **`name` is never authored.** It is derived from the directory by the adapter. Do not write `name:` in `skill.md` or in `metadata.yaml`.

4. **Authored metadata goes in `metadata.yaml`,** beside `skill.md`:
   ```yaml
   description: "<=200 chars. What it does + when to use it."
   version: "1.0.0"        # bump on every change (patch / minor / major)
   created: "YYYY-MM-DD"
   updated: "YYYY-MM-DD"
   depends_on: []          # other skills, by colon identity
   used_by: []             # reverse index
   ```

5. **The body has a `## When to invoke` section** with concrete trigger phrases.

6. **Wrapped artifacts go only to `dist/`** (git-ignored). Never commit a `SKILL.md` beside the source `skill.md`.

## Before you commit

Run the auditor — a clean library prints `Library result: PASS` with zero `[FAIL]` and zero `[WARN]`:

```
python skills/teaching-skill-builder/scripts/audit_skill.py --all
```

To wrap for deployment (output lands in git-ignored `dist/`):

```
python adapters/claude/wrap_skill.py --all -o dist/claude   # Claude .skill packages
python adapters/manus/wrap_skill.py  --all -o dist/manus    # Manus SKILL.md dirs
```

## Why these rules

Identity drift across machines and platforms is the failure mode this contract exists to prevent. Because `name` is derived from the directory, the *deployed* identity can never drift — but the *source* still can (stray frontmatter, wrong H1, missing sidecar). The auditor catches exactly those, which is why it gates CI.
