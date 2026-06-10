# Manus Adapter

The Manus adapter transforms platform-agnostic `skill.md` files from the `bieri-ai` monorepo into Manus-compatible `SKILL.md` directories ready for deployment to the Manus sandbox.

## Components

| File | Purpose |
|------|---------|
| `wrap_skill.py` | The main packaging script. Reads `skill.md`, generates YAML frontmatter, and creates a directory structure matching Manus conventions. |

## How to Package a Skill

Run the wrapper script from the repository root, pointing it to a skill directory:

```bash
python adapters/manus/wrap_skill.py skills/webdev-static-site-i18n
```

This will output:
```
✓  Wrapped: dist/manus/webdev-static-site-i18n/SKILL.md
   Deploy: copy dist/manus/webdev-static-site-i18n/ to /home/ubuntu/skills/ on Manus sandbox
```

### Batch Mode (Recommended)
You can wrap all skills in the repository at once using the `--all` flag. This is the most efficient way to prepare the entire knowledge base for a Manus session:

```bash
python adapters/manus/wrap_skill.py --all
```

### Output Location
By default, the packaged skills are saved to `dist/manus/`. You can specify a custom output directory:

```bash
python adapters/manus/wrap_skill.py --all --output /tmp/manus-deploy/
```

## How Frontmatter is Generated

Manus skills require a simple YAML frontmatter block. The adapter generates this automatically:

### 1. Name Inference
Unlike Claude, Manus uses directory-based discovery, so the adapter uses the exact directory name as the skill name:
- `skills/webdev-static-site-i18n` → `name: webdev-static-site-i18n`
- `skills/teaching-news-hooks` → `name: teaching-news-hooks`

### 2. Description Extraction
The description is extracted from the first paragraph of `skill.md` (the text immediately following the `# Title`). It is truncated to 200 characters to keep the frontmatter concise.

### 3. Metadata Overrides (`metadata.yaml`)
If you need an exact description, create a `metadata.yaml` file alongside your `skill.md`:

```yaml
# skills/webdev-static-site-i18n/metadata.yaml
description: "Exact description for Manus discovery routing."
```
The adapter will read this sidecar file and use it instead of the auto-extracted description.

## Deployment to Manus

There are two ways to deploy the generated skills to Manus:

**Method 1: Direct Sandbox Copy**
Copy the contents of `dist/manus/` directly into `/home/ubuntu/skills/` in the active Manus sandbox. Manus will auto-discover them.

**Method 2: GitHub Attachment (Preferred)**
Since `bieri-ai` is a GitHub repository, you can simply attach the repository to your Manus task. Manus will automatically scan the repository and load the skills if they are packaged correctly.
