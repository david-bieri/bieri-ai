#!/usr/bin/env python3
"""
wrap_skill.py — Manus adapter for bieri-ai skills
===================================================
Reads a platform-agnostic skill.md from the skills/ directory and wraps it
into a Manus-compatible SKILL.md with YAML frontmatter.

Usage:
    python adapters/manus/wrap_skill.py skills/<name>
    python adapters/manus/wrap_skill.py skills/<name> --output dist/manus/

The output is a directory with SKILL.md that can be placed in
/home/ubuntu/skills/<name>/ on a Manus sandbox, or attached via a GitHub
repository that Manus discovers automatically.

Manus SKILL.md format:
    ---
    name: <skill-name>
    description: <one-line description>
    ---
    <body content>
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path


# ── Metadata extraction ────────────────────────────────────────────────────

def infer_metadata(skill_dir: Path, content: str) -> dict:
    """Infer Manus YAML frontmatter from skill.md content and directory name."""
    meta = {}

    # Name: use directory name directly (Manus uses directory-based discovery)
    dir_name = skill_dir.name
    meta["name"] = dir_name

    # Description: extract from first paragraph after the title
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

    return meta


def read_metadata_sidecar(skill_dir: Path) -> dict | None:
    """Read metadata.yaml sidecar if it exists."""
    sidecar = skill_dir / "metadata.yaml"
    if not sidecar.exists():
        return None
    try:
        meta = {}
        content = sidecar.read_text()
        for line in content.strip().split("\n"):
            if ":" in line and not line.startswith("#"):
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                meta[key] = val
        return meta
    except Exception:
        return None


# ── Frontmatter generation ─────────────────────────────────────────────────

def build_frontmatter(meta: dict) -> str:
    """Build Manus-compatible YAML frontmatter string."""
    lines = [
        "---",
        f'name: {meta["name"]}',
        f'description: {meta["description"]}',
        "---",
    ]
    return "\n".join(lines)


# ── Packaging ──────────────────────────────────────────────────────────────

def wrap_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Wrap a skill directory into a Manus-compatible skill directory."""
    skill_md = skill_dir / "skill.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        sys.exit(1)

    content = skill_md.read_text()

    # Get metadata from sidecar or infer
    meta = read_metadata_sidecar(skill_dir)
    if meta is None:
        meta = infer_metadata(skill_dir, content)

    # Build the Manus SKILL.md with frontmatter
    frontmatter = build_frontmatter(meta)
    manus_content = frontmatter + "\n" + content

    # Create output directory matching Manus convention
    skill_output_dir = output_dir / meta["name"]
    skill_output_dir.mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    output_path = skill_output_dir / "SKILL.md"
    output_path.write_text(manus_content)

    # Copy any references/ and scripts/ directories
    for subdir in ("references", "scripts"):
        sub_path = skill_dir / subdir
        if sub_path.exists():
            dest = skill_output_dir / subdir
            dest.mkdir(parents=True, exist_ok=True)
            for file in sub_path.rglob("*"):
                if file.is_file() and not file.name.startswith("."):
                    target = dest / file.relative_to(sub_path)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(file.read_bytes())

    return output_path


# ── Batch mode ─────────────────────────────────────────────────────────────

def wrap_all(skills_root: Path, output_dir: Path) -> list[Path]:
    """Wrap all skills in the skills/ directory."""
    results = []
    for skill_dir in sorted(skills_root.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "skill.md").exists():
            output_path = wrap_skill(skill_dir, output_dir)
            results.append(output_path)
    return results


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Wrap a bieri-ai skill into Manus SKILL.md format"
    )
    parser.add_argument("skill_dir", type=Path, nargs="?",
                        help="Path to skill directory (e.g., skills/teaching-news-hooks). "
                             "If omitted with --all, wraps all skills.")
    parser.add_argument("--output", "-o", type=Path, default=Path("dist/manus"),
                        help="Output directory (default: dist/manus)")
    parser.add_argument("--all", action="store_true",
                        help="Wrap all skills in the skills/ directory")
    args = parser.parse_args()

    if args.all:
        # Find skills root relative to this script
        repo_root = Path(__file__).resolve().parent.parent.parent
        skills_root = repo_root / "skills"
        if not skills_root.exists():
            print(f"ERROR: {skills_root} not found")
            sys.exit(1)
        results = wrap_all(skills_root, args.output)
        print(f"✓  Wrapped {len(results)} skills into {args.output}/")
        for r in results:
            print(f"   {r.parent.name}/SKILL.md")
    else:
        if args.skill_dir is None:
            parser.error("skill_dir is required unless --all is specified")
        if not args.skill_dir.is_dir():
            print(f"ERROR: {args.skill_dir} is not a directory")
            sys.exit(1)
        output_path = wrap_skill(args.skill_dir, args.output)
        print(f"✓  Wrapped: {output_path}")
        print(f"   Deploy: copy {output_path.parent}/ to /home/ubuntu/skills/ on Manus sandbox")


if __name__ == "__main__":
    main()
