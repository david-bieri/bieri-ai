#!/usr/bin/env bash
# new-project.sh
# Scaffolds a new project: creates a SESSION_NOTES file with the project
# configuration block pre-populated and ready to upload to Claude Project
# knowledge. Run from the bieri-claude root.
#
# Usage:
#   ./tools/new-project.sh <pillar> <prefix> "<Project name>"
#
# Arguments:
#   pillar       One of: teaching | research | admin | webdev | home
#   prefix       Uppercase prefix for file naming (e.g. COURSE5174, LINEAR, AGW)
#   name         Human-readable project name (quoted if it contains spaces)
#
# Examples:
#   ./tools/new-project.sh teaching  COURSE5174 "UAP 5174 Planning Theory"
#   ./tools/new-project.sh research  LINEAR     "Linear City Dissertation"
#   ./tools/new-project.sh admin     SPIA       "SPIA White Paper"
#   ./tools/new-project.sh admin     LLI        "LLI Fall 2026 Course"
#
# Output:
#   {PREFIX}_SESSION_NOTES.md   ready to upload to Claude Project knowledge

set -euo pipefail

PILLAR="${1:-}"
PREFIX="${2:-}"
PROJECT_NAME="${3:-}"

if [[ -z "$PILLAR" || -z "$PREFIX" || -z "$PROJECT_NAME" ]]; then
    echo "Usage: ./tools/new-project.sh <pillar> <prefix> \"<Project name>\""
    echo ""
    echo "Pillars: teaching | research | admin | webdev | home"
    exit 1
fi

# Normalise
PILLAR_UPPER="${PILLAR^^}"
PREFIX_UPPER="${PREFIX^^}"
TODAY=$(date +%Y-%m-%d)
OUTPUT_FILE="${PREFIX_UPPER}_SESSION_NOTES.md"

# Dispatch targets per pillar
case "$PILLAR" in
  teaching)
    DISPATCH="  → Claude Customize   (.skill files)\n  → Project knowledge  (KB, manifest, session notes)\n  → OneDrive/Teaching/ (source files, scripts, decks)\n  → Canvas             (student-facing content)"
    REGISTRY="SKILLS_MANIFEST.md (in Project knowledge)"
    ;;
  research)
    DISPATCH="  → Project knowledge  (notes, documents)\n  → OneDrive/Research/ (papers, data, outputs)\n  → git               (code, scripts)"
    REGISTRY="RESEARCH_PROGRESS.md (create if needed)"
    ;;
  admin)
    DISPATCH="  → Project knowledge  (notes, documents)\n  → OneDrive/Admin/    (deliverables)"
    REGISTRY="{PROJECT}_PROGRESS.md + {PROJECT}_DECISIONS.md"
    ;;
  webdev)
    DISPATCH="  → git push           (code, assets, session notes)\n  → Project knowledge  (optional backup)\n  → GitHub Pages       (deployment)"
    REGISTRY="SKILLS_MANIFEST.md (in domains/webdev/)"
    ;;
  home)
    DISPATCH="  → OneDrive/Home/     (personal files)"
    REGISTRY="HOME_REGISTRY.md (create if needed)"
    ;;
  *)
    echo "ERROR: Unknown pillar '$PILLAR'. Use: teaching | research | admin | webdev | home"
    exit 1
    ;;
esac

cat > "$OUTPUT_FILE" << TEMPLATE
# ${PILLAR_UPPER} Session Notes — ${PROJECT_NAME}

**Last session:** ${TODAY}
**Topic:** (fill in after first session)
**Project:** ${PROJECT_NAME}
**Horizon:** (fill in — next deadline or milestone)

---

## Project configuration
**Prefix:** ${PREFIX_UPPER}
**Pillar:** ${PILLAR_UPPER}
**Registry:** ${REGISTRY}
**Dispatch:**
$(echo -e "$DISPATCH")
**Horizon:** (fill in)

---

## 1. Completed this session

*(fill in after first session)*

---

## 2. Pending dispatch

*(fill in after first session)*

---

## 3. Decisions made this session

*(fill in after first session)*

---

## 4. Latent issues surfaced

*(fill in after first session)*

---

## 5. Open questions

*(fill in after first session)*

---

## 6. Suggested next session

*(fill in after first session)*
TEMPLATE

echo "✓ Created: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "  1. Upload $OUTPUT_FILE to this project's Claude Project knowledge"
echo "  2. In Claude, say: 'Read ${PREFIX_UPPER}_SESSION_NOTES.md, then ...'"
echo "  3. At session end, ask Claude to update and re-upload the file"
