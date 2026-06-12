#!/usr/bin/env python3
"""
wrap_skill.py — Claude adapter for bieri-ai skills
====================================================
Reads a platform-agnostic skill.md from the skills/ directory and wraps it
into a Claude-compatible .skill package (ZIP with YAML frontmatter SKILL.md).

Usage:
    python adapters/claude/wrap_skill.py skills/<name>
    python adapters/claude/wrap_skill.py skills/<name> --output dist/claude

Identity contract:
    `name` is ALWAYS derived from the directory name (the single source of
    truth) so a sidecar can never reintroduce namespace drift:
        teaching-news-hooks      -> teaching:news-hooks
        webdev-supabase-app      -> webdev:supabase-app
        admin-cron-agent         -> admin:cron-agent
        session-handover         -> session-handover   (bare / universal)
    Authored metadata (description, version, dates, depends_on, used_by) is
    read from a metadata.yaml sidecar beside skill.md when present.
"""
import argparse
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

NAMESPACES = {"admin", "teaching", "research", "webdev", "home"}


# ── Identity ───────────────────────────────────────────────────────────────

def canonical_name(dir_name: str) -> str:
    """Derive the colon-namespaced identity from the hyphenated directory name."""
    prefix, _, rest = dir_name.partition("-")
    if prefix in NAMESPACES and rest:
        return f"{prefix}:{rest}"
    return dir_name  # bare / universal skills (e.g. session-handover)


# ── Metadata ───────────────────────────────────────────────────────────────

def read_metadata_sidecar(skill_dir: Path) -> dict:
    """Read metadata.yaml sidecar if it exists (flat key-value + simple lists)."""
    sidecar = skill_dir / "metadata.yaml"
    if not sidecar.exists():
        return {}
    meta = {}
    for line in sidecar.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip('"').strip("'")
                   for v in val[1:-1].split(",") if v.strip()]
        else:
            val = val.strip('"').strip("'")
        meta[key] = val
    return meta


def scrape_description(content: str) -> str:
    """Fallback only: first prose paragraph after the H1, capped at 200 chars."""
    lines = content.split("\n")
    desc, in_body = [], False
    for line in lines:
        if line.startswith("# ") and not in_body:
            in_body = True
            continue
        if in_body:
            if line.startswith("#") or line.startswith("---"):
                if desc:
                    break
                continue  # skip dividers/sub-headings until we hit prose
            if line.strip():
                desc.append(line.strip())
    return " ".join(desc)[:200]


def build_metadata(skill_dir: Path, content: str) -> dict:
    """name is always derived; the sidecar supplies the rest, with fallbacks."""
    side = read_metadata_sidecar(skill_dir)
    name = canonical_name(skill_dir.name)
    desc = side.get("description") or scrape_description(content) or f"Skill: {name}"
    return {
        "name": name,
        "description": desc[:200],
        "version": side.get("version", "1.0.0"),
        "created": side.get("created", str(date.today())),
        "updated": side.get("updated", str(date.today())),
        "depends_on": side.get("depends_on", []),
        "used_by": side.get("used_by", []),
    }


# ── Frontmatter ────────────────────────────────────────────────────────────

def build_frontmatter(meta: dict) -> str:
    lines = ["---", f'name: {meta["name"]}']
    desc = meta["description"]
    if len(desc) > 80:
        lines.append("description: >")
        cur = "  "
        for word in desc.split():
            if len(cur) + len(word) + 1 > 80:
                lines.append(cur)
                cur = "  " + word
            else:
                cur += (" " if cur.strip() else "") + word
        if cur.strip():
            lines.append(cur)
    else:
        lines.append(f"description: >\n  {desc}")
    lines.append(f'version: "{meta["version"]}"')
    lines.append(f'created: "{meta["created"]}"')
    lines.append(f'updated: "{meta["updated"]}"')
    lines.append(f'depends_on: {meta["depends_on"]}')
    lines.append(f'used_by: {meta["used_by"]}')
    lines.append(
        'manifest_update: "After any change to this skill, update version, '
        'updated date, and SKILLS_MANIFEST.md before closing the session."'
    )
    lines.append("---")
    return "\n".join(lines)


# ── Packaging ──────────────────────────────────────────────────────────────

def wrap_skill(skill_dir: Path, output_dir: Path) -> Path:
    skill_md = skill_dir / "skill.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        sys.exit(1)

    content = skill_md.read_text(encoding="utf-8")
    meta = build_metadata(skill_dir, content)
    claude_content = build_frontmatter(meta) + "\n" + content

    # ZIP folder = hyphenated directory name (clean, colon-free, filesystem-safe).
    zip_folder_name = skill_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{zip_folder_name}.skill"

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{zip_folder_name}/SKILL.md", claude_content)
        for subdir in ("references", "scripts", "assets"):
            sub_path = skill_dir / subdir
            if sub_path.exists():
                for file in sub_path.rglob("*"):
                    if file.is_file() and not file.name.startswith("."):
                        arcname = f"{zip_folder_name}/{subdir}/{file.relative_to(sub_path)}"
                        zf.write(file, arcname)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Wrap a bieri-ai skill into a Claude .skill package")
    parser.add_argument("skill_dir", type=Path, nargs="?", help="Path to skill directory (e.g., skills/teaching-news-hooks)")
    parser.add_argument("--output", "-o", type=Path, default=Path("dist/claude"))
    parser.add_argument("--all", action="store_true", help="Wrap every skill under skills/")
    parser.add_argument("--dry-run", action="store_true", help="Print the emitted name without writing a ZIP")
    args = parser.parse_args()

    targets = sorted(p for p in Path("skills").iterdir() if p.is_dir()) if args.all else [args.skill_dir]
    for target in targets:
        if not target.is_dir():
            print(f"ERROR: {target} is not a directory")
            sys.exit(1)
        if args.dry_run:
            content = (target / "skill.md").read_text(encoding="utf-8") if (target / "skill.md").exists() else ""
            print(f"{target.name:34s} -> name: {build_metadata(target, content)['name']}")
        else:
            out = wrap_skill(target, args.output)
            print(f"[OK]  Packaged: {out}")


if __name__ == "__main__":
    main()
