#!/usr/bin/env python3
"""
wrap_skill.py — Manus adapter for bieri-ai skills
===================================================
Reads a platform-agnostic skill.md from the skills/ directory and wraps it
into a Manus-compatible SKILL.md with YAML frontmatter.

Usage:
    python adapters/manus/wrap_skill.py skills/<name>
    python adapters/manus/wrap_skill.py --all -o dist/manus

Identity contract (matches the Claude adapter):
    `name` is ALWAYS derived from the directory (the single source of truth),
    so a sidecar can never reintroduce namespace drift:
        teaching-news-hooks -> teaching:news-hooks
        session-handover    -> session-handover   (bare / universal)
    Authored metadata (description, version, depends_on, used_by) is read from
    a metadata.yaml sidecar when present. The OUTPUT directory uses the
    hyphenated directory name (filesystem-safe), while frontmatter `name`
    carries the colon identity.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

NAMESPACES = {"admin", "teaching", "research", "webdev", "home"}


def canonical_name(dir_name: str) -> str:
    """Derive the colon-namespaced identity from the hyphenated directory name."""
    prefix, _, rest = dir_name.partition("-")
    if prefix in NAMESPACES and rest:
        return f"{prefix}:{rest}"
    return dir_name  # bare / universal skills (e.g. session-handover)


def read_metadata_sidecar(skill_dir: Path) -> dict:
    """Read metadata.yaml sidecar if present (flat keys + simple flow lists)."""
    sidecar = skill_dir / "metadata.yaml"
    if not sidecar.exists():
        return {}
    meta = {}
    for line in sidecar.read_text().splitlines():
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
    desc, in_body = [], False
    for line in content.split("\n"):
        if line.startswith("# ") and not in_body:
            in_body = True
            continue
        if in_body:
            if line.startswith("#") or line.startswith("---"):
                if desc:
                    break
                continue
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
        "depends_on": side.get("depends_on", []),
        "used_by": side.get("used_by", []),
    }


def build_frontmatter(meta: dict) -> str:
    lines = [
        "---",
        f'name: {meta["name"]}',
        f'description: {meta["description"]}',
        f'version: "{meta["version"]}"',
        f'depends_on: {meta["depends_on"]}',
        f'used_by: {meta["used_by"]}',
        "---",
    ]
    return "\n".join(lines)


def wrap_skill(skill_dir: Path, output_dir: Path) -> Path:
    skill_md = skill_dir / "skill.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        sys.exit(1)

    content = skill_md.read_text()
    meta = build_metadata(skill_dir, content)
    manus_content = build_frontmatter(meta) + "\n" + content

    # Output dir uses the hyphenated directory name (filesystem-safe, colon-free).
    skill_output_dir = output_dir / skill_dir.name
    skill_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = skill_output_dir / "SKILL.md"
    output_path.write_text(manus_content)

    for subdir in ("references", "scripts", "assets"):
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


def wrap_all(skills_root: Path, output_dir: Path) -> list:
    results = []
    for skill_dir in sorted(skills_root.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "skill.md").exists():
            results.append(wrap_skill(skill_dir, output_dir))
    return results


def main():
    parser = argparse.ArgumentParser(description="Wrap a bieri-ai skill into Manus SKILL.md format")
    parser.add_argument("skill_dir", type=Path, nargs="?",
                        help="Path to skill directory (omit with --all)")
    parser.add_argument("--output", "-o", type=Path, default=Path("dist/manus"))
    parser.add_argument("--all", action="store_true", help="Wrap all skills under skills/")
    args = parser.parse_args()

    if args.all:
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


if __name__ == "__main__":
    main()
