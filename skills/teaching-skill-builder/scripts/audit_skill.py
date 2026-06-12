#!/usr/bin/env python3
"""
audit_skill.py — Compliance checker for bieri-ai skills
========================================================
Usage:
    python audit_skill.py <skill-folder>     # audit a source skill dir (skill.md + metadata.yaml)
    python audit_skill.py <skill.skill>      # audit a wrapped .skill/.zip artifact
    python audit_skill.py --all              # audit every source skill dir under skills/

Validates the bieri-ai contract (see CONTRIBUTING.md):
  - source skill.md has NO frontmatter (adapters add it)
  - H1 matches the canonical colon identity derived from the directory
  - body has a '## When to invoke' section
  - metadata.yaml carries description (<=200), version, and the graph
  - metadata.yaml does NOT set `name` (it is always derived)
For wrapped artifacts, checks the emitted frontmatter (name <=64, description <=200).
"""
import re
import sys
import zipfile
from pathlib import Path

NAMESPACES = {"admin", "teaching", "research", "webdev", "home"}


def canonical_name(dir_name: str) -> str:
    prefix, _, rest = dir_name.partition("-")
    if prefix in NAMESPACES and rest:
        return f"{prefix}:{rest}"
    return dir_name


# ── Wrapped-artifact frontmatter audit (Claude .skill ZIP) ──────────────────

def audit_frontmatter(content: str) -> list:
    parts = content.split("---", 2)
    if len(parts) < 3:
        return ["FAIL: wrapped SKILL.md has no frontmatter block"]
    fm = parts[1]
    body = parts[2]
    issues = []
    name_m = re.search(r'^name:\s*(.+)$', fm, re.M)
    if not name_m:
        issues.append("FAIL: missing required field 'name'")
    elif len(name_m.group(1).strip()) > 64:
        issues.append(f"FAIL: name too long ({len(name_m.group(1).strip())} chars, max 64)")
    desc_block = re.search(r'^description: >\n((?:  .+\n?)+)', fm, re.M)
    if desc_block:
        desc = re.sub(r'\s+', ' ', desc_block.group(1).replace('\n', '').strip())
    else:
        single = re.search(r'^description:\s*(.+)$', fm, re.M)
        desc = single.group(1).strip() if single else None
    if desc is None:
        issues.append("FAIL: missing required field 'description'")
    elif len(desc) > 200:
        issues.append(f"FAIL: description too long ({len(desc)} chars, max 200)")
    if "## When to invoke" not in body:
        issues.append("WARN: missing '## When to invoke' section in body")
    return issues


# ── Source-dir audit (skill.md + metadata.yaml, the new contract) ───────────

def audit_source_dir(skill_dir: Path) -> tuple:
    name = skill_dir.name
    issues = []
    src = skill_dir / "skill.md"
    if not src.exists():
        return name, ["FAIL: skill.md not found (orphan? wrapped-only skills need a source)"]
    content = src.read_text(encoding="utf-8")

    # 1. No frontmatter in source
    if content.lstrip().startswith("---"):
        issues.append("FAIL: skill.md must NOT contain YAML frontmatter (adapters add it)")

    # 2. H1 matches canonical identity
    h1 = re.search(r'^#\s+(.+)$', content, re.M)
    expected = canonical_name(name)
    if not h1:
        issues.append("FAIL: no H1 title found")
    elif h1.group(1).strip() != expected:
        issues.append(f"FAIL: H1 '{h1.group(1).strip()}' != canonical identity '{expected}'")

    # 3. When to invoke
    if "## When to invoke" not in content:
        issues.append("WARN: missing '## When to invoke' section")

    # 4. metadata.yaml
    side = skill_dir / "metadata.yaml"
    if not side.exists():
        issues.append("FAIL: metadata.yaml sidecar not found")
    else:
        meta = side.read_text(encoding="utf-8")
        if re.search(r'^name:\s*', meta, re.M):
            issues.append("WARN: metadata.yaml should NOT set 'name' (it is derived from the directory)")
        dm = re.search(r'^description:\s*"?(.+?)"?\s*$', meta, re.M)
        if not dm:
            issues.append("FAIL: metadata.yaml missing 'description'")
        elif len(dm.group(1)) > 200:
            issues.append(f"FAIL: description too long ({len(dm.group(1))} chars, max 200)")
        if not re.search(r'^version:\s*', meta, re.M):
            issues.append("WARN: metadata.yaml missing 'version'")
    return name, issues


def audit_zip(zip_path: Path) -> tuple:
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        roots = {n.split("/")[0] for n in names if n.split("/")[0]}
        if len(roots) != 1:
            return zip_path.stem, [f"FAIL: ZIP must have exactly one root folder, found: {roots}"]
        root = list(roots)[0]
        skill_md = f"{root}/SKILL.md"
        if skill_md not in names:
            return root, ["FAIL: SKILL.md not found in ZIP root folder"]
        return root, audit_frontmatter(z.read(skill_md).decode("utf-8"))


def report(name: str, issues: list) -> bool:
    print(f"\nAudit: {name}\n" + "=" * 50)
    fails = [i for i in issues if i.startswith("FAIL")]
    warns = [i for i in issues if i.startswith("WARN")]
    if not issues:
        print("[OK]  All checks passed")
    else:
        for f in fails:
            print(f"  [FAIL]  {f[5:]}")
        for w in warns:
            print(f"  [WARN]  {w[5:]}")
    return len(fails) == 0


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python audit_skill.py <skill-folder | .skill | --all>")
        sys.exit(1)

    if args[0] == "--all":
        skills_root = Path(__file__).resolve().parents[3] / "skills"
        all_ok = True
        for d in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            name, issues = audit_source_dir(d)
            all_ok &= report(name, issues)
        print("\n" + ("=" * 50) + f"\nLibrary result: {'PASS' if all_ok else 'FAIL'}")
        sys.exit(0 if all_ok else 1)

    target = Path(args[0])
    if not target.exists():
        print(f"ERROR: {target} not found")
        sys.exit(1)
    if target.suffix in (".skill", ".zip"):
        name, issues = audit_zip(target)
    elif target.is_dir():
        name, issues = audit_source_dir(target)
    else:
        print(f"ERROR: {target} must be a folder or a .skill/.zip file")
        sys.exit(1)
    ok = report(name, issues)
    print(f"\nResult: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
