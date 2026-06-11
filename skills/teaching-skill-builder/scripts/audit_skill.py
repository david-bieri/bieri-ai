#!/usr/bin/env python3
"""
audit_skill.py — Compliance checker for teaching: namespace skills
Usage: python audit_skill.py <skill-folder>
       python audit_skill.py <skill.skill>   (ZIP file)

Checks against official Anthropic spec:
  https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
"""

import re
import sys
import zipfile
from pathlib import Path


def audit_from_text(content: str, skill_name: str = "?") -> list[str]:
    """Return list of compliance issues. Empty list = pass."""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return ["Malformed SKILL.md: could not find closing frontmatter ---"]

    fm = parts[1]
    body = parts[2]
    issues = []

    # ── Required: name (≤64 chars) ─────────────────────────────────────
    name_m = re.search(r'^name:\s*(.+)$', fm, re.M)
    if not name_m:
        issues.append("FAIL: missing required field 'name'")
    else:
        name = name_m.group(1).strip()
        if len(name) > 64:
            issues.append(f"FAIL: name too long ({len(name)} chars, max 64)")

    # ── Required: description (≤200 chars) ─────────────────────────────
    desc_m = re.search(r'^description: >\n((?:  .+\n?)+)', fm, re.M)
    if not desc_m:
        # Try single-line description
        desc_single = re.search(r'^description:\s*(.+)$', fm, re.M)
        if not desc_single:
            issues.append("FAIL: missing required field 'description'")
        else:
            desc = desc_single.group(1).strip()
            if len(desc) > 200:
                issues.append(f"FAIL: description too long ({len(desc)} chars, max 200)")
    else:
        desc = re.sub(r'\s+', ' ', desc_m.group(1).replace('\n', '').strip())
        if len(desc) > 200:
            issues.append(f"FAIL: description too long ({len(desc)} chars, max 200)")

    # ── Optional: dependencies format (should be package specifiers) ───
    dep_m = re.search(r'^dependencies:\s*(.+)$', fm, re.M)
    if dep_m:
        dep_val = dep_m.group(1).strip().strip('"\'')
        # Warn if it looks like skill names rather than packages
        if dep_val.startswith("teaching:"):
            issues.append(
                "WARN: 'dependencies' should list software packages (e.g. python-pptx>=0.6), "
                "not skill names — use 'depends_on' for skill-to-skill references"
            )

    # ── Body: When to invoke section ───────────────────────────────────
    if "## When to invoke" not in body:
        issues.append("WARN: missing '## When to invoke' section in body")

    return issues


def audit_folder(skill_dir: Path) -> tuple[str, list[str]]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return str(skill_dir.name), ["FAIL: SKILL.md not found"]
    return str(skill_dir.name), audit_from_text(skill_md.read_text(), skill_dir.name)


def audit_zip(zip_path: Path) -> tuple[str, list[str]]:
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()

        # Check folder-as-root structure
        root_items = set()
        for n in names:
            parts = n.split("/")
            if parts[0]:
                root_items.add(parts[0])

        if len(root_items) != 1:
            return zip_path.stem, [f"FAIL: ZIP must have exactly one root folder, found: {root_items}"]

        root_folder = list(root_items)[0]

        # Find SKILL.md
        skill_md_path = f"{root_folder}/SKILL.md"
        if skill_md_path not in names:
            return root_folder, ["FAIL: SKILL.md not found in ZIP root folder"]

        content = z.read(skill_md_path).decode("utf-8")
        issues = audit_from_text(content, root_folder)
        return root_folder, issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python audit_skill.py <skill-folder-or-zip>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"ERROR: {target} not found")
        sys.exit(1)

    if target.suffix in (".skill", ".zip"):
        name, issues = audit_zip(target)
    elif target.is_dir():
        name, issues = audit_folder(target)
    else:
        print(f"ERROR: {target} must be a folder or a .skill/.zip file")
        sys.exit(1)

    print(f"\nAudit: {name}")
    print("=" * 50)

    fails = [i for i in issues if i.startswith("FAIL")]
    warns = [i for i in issues if i.startswith("WARN")]

    if not issues:
        print("✓  All checks passed")
    else:
        for f in fails:
            print(f"  ✗  {f[5:]}")
        for w in warns:
            print(f"  ⚠  {w[5:]}")

    print()
    if fails:
        print(f"Result: FAIL ({len(fails)} error(s), {len(warns)} warning(s))")
        sys.exit(1)
    elif warns:
        print(f"Result: PASS with {len(warns)} warning(s)")
    else:
        print("Result: PASS")


if __name__ == "__main__":
    main()
