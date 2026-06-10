#!/usr/bin/env python3
"""
wrap_skill.py — Claude adapter for bieri-ai skills
====================================================
Reads a platform-agnostic skill.md from the skills/ directory and wraps it
into a Claude-compatible .skill package (ZIP with YAML frontmatter SKILL.md).

Usage:
    python adapters/claude/wrap_skill.py skills/<name>
    python adapters/claude/wrap_skill.py skills/<name> --output dist/

The output is a .skill ZIP file ready for upload to Claude Desktop:
    Claude Desktop → Cowork → Customize → Skills → + → upload

Frontmatter fields are read from a metadata.yaml sidecar file if present,
or inferred from the skill.md content and directory name.
"""
import argparse
import re
import sys
import zipfile
from datetime import date
from pathlib import Path


# ── Metadata extraction ────────────────────────────────────────────────────

def infer_metadata(skill_dir: Path, content: str) -> dict:
    """Infer Claude YAML frontmatter from skill.md content and directory name."""
    meta = {}

    # Name: derive from directory name
    dir_name = skill_dir.name
    # Convert "teaching-news-hooks" → "course:news-hooks"
    # Convert "webdev-static-site-i18n" → "webdev:static-site-i18n"
    # Convert "session-handover" → "session-handover"
    if dir_name.startswith("teaching-"):
        meta["name"] = "course:" + dir_name[len("teaching-"):]
    elif dir_name.startswith("webdev-"):
        meta["name"] = dir_name  # keep as-is for webdev skills
    else:
        meta["name"] = dir_name

    # Description: extract from first paragraph after the title
    # Look for text between the title and the first ## heading
    lines = content.split("\n")
    desc_lines = []
    in_desc = False
    for line in lines:
        if line.startswith("# ") and not in_desc:
            in_desc = True
            continue
        if in_desc:
            if line.startswith("##") or line.startswith("---"):
                break
            if line.strip():
                desc_lines.append(line.strip())
    desc = " ".join(desc_lines)[:200]
    meta["description"] = desc if desc else f"Skill: {dir_name}"

    # Version and dates
    meta["version"] = "1.0.0"
    meta["created"] = str(date.today())
    meta["updated"] = str(date.today())

    # Dependencies
    meta["depends_on"] = []
    meta["used_by"] = []

    return meta


def read_metadata_sidecar(skill_dir: Path) -> dict | None:
    """Read metadata.yaml sidecar if it exists."""
    sidecar = skill_dir / "metadata.yaml"
    if not sidecar.exists():
        return None
    try:
        # Simple YAML parsing for flat key-value pairs
        meta = {}
        content = sidecar.read_text()
        for line in content.strip().split("\n"):
            if ":" in line and not line.startswith("#"):
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val.startswith("[") and val.endswith("]"):
                    # Parse simple list
                    val = [v.strip().strip('"').strip("'")
                           for v in val[1:-1].split(",") if v.strip()]
                meta[key] = val
        return meta
    except Exception:
        return None


# ── Frontmatter generation ─────────────────────────────────────────────────

def build_frontmatter(meta: dict) -> str:
    """Build Claude-compatible YAML frontmatter string."""
    lines = ["---"]
    lines.append(f'name: {meta["name"]}')

    # Multi-line description (Claude format)
    desc = meta["description"]
    if len(desc) > 80:
        lines.append("description: >")
        # Wrap at ~78 chars with 2-space indent
        words = desc.split()
        current_line = "  "
        for word in words:
            if len(current_line) + len(word) + 1 > 80:
                lines.append(current_line)
                current_line = "  " + word
            else:
                current_line += (" " if current_line.strip() else "") + word
        if current_line.strip():
            lines.append(current_line)
    else:
        lines.append(f"description: >{chr(10)}  {desc}")

    lines.append(f'version: "{meta.get("version", "1.0.0")}"')
    lines.append(f'created: "{meta.get("created", str(date.today()))}"')
    lines.append(f'updated: "{meta.get("updated", str(date.today()))}"')

    depends = meta.get("depends_on", [])
    lines.append(f'depends_on: {depends}')

    used_by = meta.get("used_by", [])
    lines.append(f'used_by: {used_by}')

    lines.append(
        'manifest_update: "After any change to this skill, update version, '
        'updated date, and SKILLS_MANIFEST.md before closing the session."'
    )
    lines.append("---")
    return "\n".join(lines)


# ── Packaging ──────────────────────────────────────────────────────────────

def wrap_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Wrap a skill directory into a Claude .skill ZIP package."""
    skill_md = skill_dir / "skill.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        sys.exit(1)

    content = skill_md.read_text()

    # Get metadata from sidecar or infer
    meta = read_metadata_sidecar(skill_dir)
    if meta is None:
        meta = infer_metadata(skill_dir, content)

    # Build the Claude SKILL.md with frontmatter
    frontmatter = build_frontmatter(meta)
    claude_content = frontmatter + "\n" + content

    # Determine the folder name inside the ZIP (Claude convention)
    zip_folder_name = meta["name"].replace(":", "")  # "course:news-hooks" → "coursenews-hooks"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{zip_folder_name}.skill"

    # Build ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add SKILL.md
        zf.writestr(f"{zip_folder_name}/SKILL.md", claude_content)

        # Add any references/ and scripts/ directories
        for subdir in ("references", "scripts"):
            sub_path = skill_dir / subdir
            if sub_path.exists():
                for file in sub_path.rglob("*"):
                    if file.is_file() and not file.name.startswith("."):
                        arcname = f"{zip_folder_name}/{subdir}/{file.relative_to(sub_path)}"
                        zf.write(file, arcname)

    return output_path


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Wrap a bieri-ai skill into a Claude .skill package"
    )
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory (e.g., skills/teaching-news-hooks)")
    parser.add_argument("--output", "-o", type=Path, default=Path("dist/claude"),
                        help="Output directory for .skill file (default: dist/claude)")
    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"ERROR: {args.skill_dir} is not a directory")
        sys.exit(1)

    output_path = wrap_skill(args.skill_dir, args.output)
    print(f"✓  Packaged: {output_path}")
    print(f"   Install: Claude Desktop → Cowork → Customize → Skills → + → upload")


if __name__ == "__main__":
    main()
