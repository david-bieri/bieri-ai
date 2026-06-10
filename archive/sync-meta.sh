#!/usr/bin/env bash
# sync-meta.sh
# Run from inside a pillar repo (bieri-teaching, bieri-research, bieri-admin)
# to pull the latest universal tools and templates from bieri-claude.
#
# Usage:
#   cd ~/GitHub/bieri-teaching && ./sync-meta.sh
#
# Assumes bieri-claude is a sibling directory:
#   ~/GitHub/bieri-claude/
#   ~/GitHub/bieri-teaching/   ← run from here

set -euo pipefail

META_REPO="$(cd "$(dirname "$0")/../bieri-claude" && pwd)"

if [[ ! -d "$META_REPO" ]]; then
    echo "ERROR: bieri-claude not found at $META_REPO"
    echo "Clone it alongside this repo: git clone ... ~/GitHub/bieri-claude"
    exit 1
fi

echo "Syncing from $META_REPO ..."

# Universal skill
mkdir -p shared/session-handover
cp -r "$META_REPO/shared-skills/session-handover/." shared/session-handover/
echo "  ✓ shared/session-handover/"

# Tools
cp "$META_REPO/tools/audit_skill.py"  shared/audit_skill.py
cp "$META_REPO/tools/package.sh"      package.sh
chmod +x package.sh
echo "  ✓ shared/audit_skill.py"
echo "  ✓ package.sh"

# Architecture and bootstrap
mkdir -p shared/architecture
cp -r "$META_REPO/architecture/."     shared/architecture/
cp "$META_REPO/BIERI_CLAUDE.md"       BIERI_CLAUDE.md
echo "  ✓ shared/architecture/"
echo "  ✓ BIERI_CLAUDE.md"

echo ""
echo "Done. Review changes with: git diff --stat"
echo "Commit with: git add -A && git commit -m \"sync: meta tools from bieri-claude\""
