#!/usr/bin/env bash
# package.sh
# Packages all skills in skills/ and the shared session-handover into dist/
# Runs audit_skill.py on each .skill file after packaging.
#
# Usage:
#   ./package.sh              # package everything
#   ./package.sh course-build-kb  # package one skill by folder name
#
# Output: dist/*.skill  (ready to install via Cowork → Customize → Skills)

set -euo pipefail

SKILLS_DIR="./skills"
SHARED_DIR="./shared"
DIST_DIR="./dist"
AUDIT="$SHARED_DIR/audit_skill.py"
EXCLUDE="-x *.DS_Store */.git/* */__pycache__/* *.pyc *.swp"

# ── helpers ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; RESET='\033[0m'
pass() { echo -e "${GREEN}✓${RESET} $1"; }
fail() { echo -e "${RED}✗${RESET} $1"; exit 1; }

mkdir -p "$DIST_DIR"

package_one() {
    local src="$1"          # e.g. skills/course-compose-slides
    local name="$2"         # e.g. course-compose-slides
    local out="$DIST_DIR/${name}.skill"

    zip -r "$out" "$src/" $EXCLUDE > /dev/null
    python3 "$AUDIT" "$out" > /dev/null 2>&1 \
        && pass "$name  →  $out" \
        || { echo ""; python3 "$AUDIT" "$out"; fail "$name failed audit — fix before installing"; }
}

# ── main ─────────────────────────────────────────────────────────────────────
if [[ $# -eq 1 ]]; then
    # Package a single named skill
    target="$1"
    if [[ -d "$SKILLS_DIR/$target" ]]; then
        package_one "$SKILLS_DIR/$target" "$target"
    elif [[ "$target" == "session-handover" ]]; then
        package_one "$SHARED_DIR/session-handover" "session-handover"
    else
        fail "Unknown skill: $target"
    fi
else
    # Package all skills + session-handover
    echo "Packaging skills..."
    for skill_dir in "$SKILLS_DIR"/*/; do
        name=$(basename "$skill_dir")
        package_one "$skill_dir" "$name"
    done

    echo "Packaging shared skill..."
    package_one "$SHARED_DIR/session-handover" "session-handover"

    count=$(ls "$DIST_DIR"/*.skill 2>/dev/null | wc -l | tr -d ' ')
    echo ""
    echo "Done — $count skills packaged in $DIST_DIR/"
fi
