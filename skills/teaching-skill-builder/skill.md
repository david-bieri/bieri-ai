
# teaching:skill-builder

Creates, audits, and maintains teaching skills in the `teaching:` namespace.

---

## When to invoke

Trigger on: "build a skill from this workflow"; "package what we just did into a
skill"; "create a new skill"; "update skill X"; "audit my skills against the spec";
"run compliance check"; "update the manifest"; "add version control to skills".
Also triggers when any skill in the library has been changed and SKILLS_MANIFEST.md
needs updating.

---

## Official spec requirements (Anthropic)

Source: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

| Field | Requirement |
|-------|-------------|
| `name` | Required · ≤ 64 characters |
| `description` | Required · **≤ 200 characters** — Claude uses this to decide when to invoke |
| `dependencies` | Optional · software packages only (e.g. `python-pptx>=0.6`) |

**ZIP structure (required):**
```
skill-name.skill  (ZIP)
└── skill-name/           ← folder at ZIP root, name matches skill
    ├── SKILL.md
    ├── references/       (optional)
    └── scripts/          (optional)
```
Files must NOT be directly in the ZIP root — the skill folder must be the root.

**Code execution** must be enabled in Claude settings for scripts to run.

---

## Our conventions (bieri-ai contract)

> **Source of truth:** `CONTRIBUTING.md` at the repo root. The rules below are the teaching-domain view of it.

`skill.md` is pure Markdown with **no YAML frontmatter** — the adapter adds the
frontmatter at wrap time, and derives `name` from the directory (`teaching-news-hooks`
→ `teaching:news-hooks`), so identity can never drift. Authored metadata lives in a
`metadata.yaml` sidecar next to `skill.md`:

```yaml
# metadata.yaml — name is NOT set here (adapter derives it from the directory)
description: "≤200 chars. Core trigger. Use for X, Y, Z."
version: "1.0.1"          # semantic: major.minor.patch
created: "YYYY-MM-DD"      # immutable
updated: "YYYY-MM-DD"      # bump on every change
depends_on: []             # other skills (colon identity) this one calls or requires
used_by: []                # reverse index — which skills call this one
```

`depends_on`/`used_by` are the composition graph — they now flow through the adapter
into the deployed artifact, so keep them accurate.

**Version bumping convention:**
- **Patch** (1.0.0 → 1.0.1): bug fixes, wording tweaks, compliance corrections
- **Minor** (1.0.0 → 1.1.0): new sections, added functionality, no breaking changes
- **Major** (1.0.0 → 2.0.0): structural rewrites, breaking output changes

---

## Workflow for creating a new skill

### Step 1 — Identify and scope
Extract from the conversation:
- What repeatable workflow does this capture?
- Which courses / contexts does it apply to?
- What are the inputs and outputs?
- Does it depend on other skills or on the KB being present?

### Step 2 — Write `skill.md` (no frontmatter) + `metadata.yaml`

`skill.md` is pure Markdown, starting at the H1 — no frontmatter:

```
# teaching:skill-name

[One-line summary]

---

## When to invoke

[Concrete trigger phrases and contexts — the overflow from the 200-char description]

---

## [Workflow sections…]
```

Then a `metadata.yaml` sidecar carries the authored metadata (copy `templates/metadata.yaml`):

```yaml
description: "≤200 chars. Core trigger statement. Use for X, Y, Z."
version: "1.0.0"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
depends_on: [list of skills required, by colon identity]
used_by: []
```

`name` is **not** written anywhere — the adapter derives `teaching:skill-name` from the
`teaching-skill-name` directory.

**Description writing rule:** Write the description last, after the body is complete.
Distil to ≤200 chars: name the task, name the trigger contexts, name any hard
prerequisite (e.g. "Requires KB in Project knowledge"). Cut ruthlessly — the body
carries the detail.

### Step 3 — Add bundled resources if needed

- `references/` — reference files Claude reads on demand (style guides, specs)
- `scripts/` — executable code (Python, Node.js) Claude can run

Reference scripts from SKILL.md with a clear pointer: *"Read references/X.md before
proceeding."*

### Step 4 — Run compliance audit

```bash
python scripts/audit_skill.py /path/to/skill-folder
```

Or run the inline audit (see below). Fix any failures before packaging.

### Step 5 — Package

```bash
cd /home/claude/skills
zip -r "/mnt/user-data/outputs/skill-name.skill" "skill-folder-name/" -x "*.DS_Store"
```

The folder name inside the ZIP must match the skill directory name.

### Step 6 — Update SKILLS_MANIFEST.md (mandatory)

Per the manifest enforcement rule:
1. Bump `version` and `updated` in SKILL.md frontmatter
2. Update Installed Skills table in manifest
3. Update or add the skill description block
4. Update dependency graph if needed
5. Add Update Log entry

**Do not skip this step.**

---

## Workflow for updating an existing skill

1. Edit `skills/<name>/SKILL.md` (and any bundled files)
2. Bump `version` (patch/minor/major) and `updated` date in frontmatter
3. `git add -A && git commit -m "<namespace>:<name> vX.Y.Z: change description"`
4. `./package.sh <name>` — runs audit automatically
5. Install: Claude Desktop → Cowork → Customize → Skills → + → upload from `dist/`
6. Update `SKILLS_MANIFEST.md` and Update Log
7. Present updated `.skill` file if sharing

Never install without the audit passing. Never close the session without
updating the manifest.

---

## Inline compliance audit

Run this to check a skill folder before packaging:

```python
import zipfile, re
from pathlib import Path

def audit_skill(skill_dir: str):
    path = Path(skill_dir)
    content = (path / "SKILL.md").read_text()
    parts = content.split("---", 2)
    fm = parts[1]
    issues = []

    # name ≤64
    name_m = re.search(r'^name:\s*(.+)$', fm, re.M)
    name = name_m.group(1).strip() if name_m else ""
    if not name: issues.append("Missing required: name")
    elif len(name) > 64: issues.append(f"name too long: {len(name)} (max 64)")

    # description ≤200
    desc_m = re.search(r'^description: >\n((?:  .+\n?)+)', fm, re.M)
    if not desc_m:
        issues.append("Missing required: description")
    else:
        desc = re.sub(r'\s+', ' ', desc_m.group(1).replace('\n','').strip())
        if len(desc) > 200:
            issues.append(f"description too long: {len(desc)} chars (max 200)")

    # When to invoke section
    body = parts[2] if len(parts) >= 3 else ""
    if "## When to invoke" not in body:
        issues.append("Missing 'When to invoke' section")

    return issues
```

The bundled `scripts/audit_skill.py` runs this as a command-line tool.

---


---

## When a skill is identified but not built

Not every skill idea should be built immediately. When a session surfaces a
skill candidate that you decide to defer:

1. **Add it to the manifest** — `SKILLS_MANIFEST.md` → `## Candidate skills`
   section. Include: name, what it does, why it was deferred, and a concrete
   **trigger condition** ("build when X happens", not "someday").
2. **Add pending updates the same way** — if an *existing* skill needs a
   future version bump, add it to `## Pending updates` with the target version
   and what needs to change.
3. **Don't leave it only in conversation** — anything discussed but not recorded
   in the manifest is effectively lost when the session ends.

The manifest is the complete picture: installed → pending → candidate.
A skill idea without a trigger condition is an aspiration; with one, it's a plan.

## Repo structure

Skills live as source in the pillar repo, packaged on demand:

```
~/GitHub/bieri-teaching/          ← Teaching pillar repo
  skills/<skill-name>/            ← source (tracked in git)
    SKILL.md
    references/ or scripts/
  dist/<skill-name>.skill         ← packaged artifact (git-ignored)
  package.sh                      ← packaging script (synced from bieri-claude)
  shared/
    session-handover/             ← synced from bieri-claude
    audit_skill.py                ← synced from bieri-claude

~/GitHub/bieri-claude/            ← meta repo (universal infrastructure)
  tools/package.sh
  tools/audit_skill.py
  tools/sync-meta.sh
  shared-skills/session-handover/
```

## Known skills in the teaching: library

| Skill | Purpose |
|-------|---------|
| `teaching:news-hooks` | "In the news" slide search and formatting |
| `teaching:build-kb` | PPTX → KB extraction via build_kb.py |
| `teaching:video-scripts` | Narration script generation (130 wpm) |
| `teaching:compose-slides` | Lecture deck composition in house style |
| `teaching:assess-from-kb` | Assessment generation from KB content |
| `teaching:skill-builder` | This skill — library creation and maintenance |

Manifest: `SKILLS_MANIFEST.md` in Project knowledge.
Storage: `OneDrive - Virginia Tech/Teaching/Skills/`
