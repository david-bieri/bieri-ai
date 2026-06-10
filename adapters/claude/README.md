# Claude Adapter

The Claude adapter transforms platform-agnostic `skill.md` files from the `bieri-ai` monorepo into `.skill` ZIP packages suitable for upload to Claude Desktop Projects.

## Components

| File | Purpose |
|------|---------|
| `wrap_skill.py` | The main packaging script. Reads `skill.md`, generates YAML frontmatter, and creates the `.skill` ZIP archive. |
| `audit_skill.py` | Compliance checker. Verifies that the generated `.skill` file meets Anthropic's official skill format specifications. |
| `package.sh` | Legacy shell script (deprecated, replaced by `wrap_skill.py`). |

## How to Package a Skill

Run the wrapper script from the repository root, pointing it to a skill directory:

```bash
python adapters/claude/wrap_skill.py skills/teaching-news-hooks
```

This will output:
```
✓  Packaged: dist/claude/coursenews-hooks.skill
   Install: Claude Desktop → Cowork → Customize → Skills → + → upload
```

### Output Location
By default, the `.skill` ZIP file is saved to `dist/claude/`. You can specify a custom output directory:

```bash
python adapters/claude/wrap_skill.py skills/teaching-news-hooks --output /tmp/my-skills/
```

## How Frontmatter is Generated

Claude skills require YAML frontmatter containing metadata (name, description, version, dependencies). The adapter generates this automatically:

### 1. Name Inference
The adapter infers the Claude namespace from the directory name:
- `skills/teaching-news-hooks` → `name: course:news-hooks`
- `skills/webdev-static-site-i18n` → `name: webdev:static-site-i18n`
- `skills/session-handover` → `name: session-handover`

### 2. Description Extraction
The description is extracted from the first paragraph of `skill.md` (the text immediately following the `# Title`). It is truncated to 200 characters to comply with Claude's limits.

### 3. Metadata Overrides (`metadata.yaml`)
If you need specific versions, dependencies, or exact descriptions, create a `metadata.yaml` file alongside your `skill.md`:

```yaml
# skills/teaching-news-hooks/metadata.yaml
version: "1.0.1"
depends_on: ["course:compose-slides"]
description: "Custom description that overrides the auto-extracted one."
```
The adapter will read this sidecar file and merge it into the generated frontmatter.

## Compliance Auditing

You can verify that any generated `.skill` file is compliant with Claude's requirements using the audit script:

```bash
python adapters/claude/audit_skill.py dist/claude/coursenews-hooks.skill
```

This checks for:
- Required fields (`name`, `description`)
- Character limits (name ≤ 64, description ≤ 200)
- Proper ZIP root folder structure
- Presence of `## When to invoke` section in the body
