# ============================================================
# BIERI CLAUDE — FULL REPO SETUP
# Run these commands in PowerShell after downloading all files
# from the Claude session to ~\Downloads\
#
# ORDER MATTERS: bieri-claude must be done first.
# ============================================================

# Assumes:
#   - Git is installed
#   - Downloaded files are in ~\Downloads\
#   - GitHub repos already created (empty) at:
#       https://github.com/david-bieri/bieri-claude
#       https://github.com/david-bieri/bieri-teaching
#       https://github.com/david-bieri/bieri-research
#       https://github.com/david-bieri/bieri-admin

$downloads = "$env:USERPROFILE\Downloads"
$github    = "$env:USERPROFILE\GitHub"

# Create GitHub root folder if it doesn't exist
New-Item -ItemType Directory -Path $github -Force | Out-Null



# ============================================================
# REPO 1: bieri-claude  (meta — do this first)
# ============================================================

cd $github
git clone https://github.com/david-bieri/bieri-claude.git
cd bieri-claude

# Extract the bieri-claude.zip — it contains a bieri-claude\ subfolder
Expand-Archive -Path "$downloads\bieri-claude.zip" `
               -DestinationPath "$downloads\bieri-claude-extract" -Force

# Copy all extracted contents into the cloned repo
Copy-Item -Path "$downloads\bieri-claude-extract\bieri-claude\*" `
          -Destination "." -Recurse -Force

# Clean up temp extract
Remove-Item -Path "$downloads\bieri-claude-extract" -Recurse -Force

# Commit and push
git add -A
git commit -m "init: bieri-claude meta repo — universal tools, session-handover, templates, architecture"
git push -u origin main

Write-Host "bieri-claude done." -ForegroundColor Green



# ============================================================
# REPO 2: bieri-teaching
# ============================================================

cd $github
git clone https://github.com/david-bieri/bieri-teaching.git
cd bieri-teaching

# Create folder structure
New-Item -ItemType Directory -Path `
    skills, scripts, manifests, dist, `
    "shared\session-handover", "shared\architecture" -Force | Out-Null

# ── Root files ──
Copy-Item "$downloads\README_bieri_teaching.md"  "README.md"
Copy-Item "$downloads\gitignore_template.txt" ".gitignore"
Copy-Item "$downloads\BIERI_CLAUDE.md"           "BIERI_CLAUDE.md"

# ── Scripts ──
Copy-Item "$downloads\build_kb.py"               "scripts\build_kb.py"

# ── Manifests ──
Copy-Item "$downloads\SKILLS_MANIFEST.md"        "manifests\SKILLS_MANIFEST.md"

# ── Sync shared tools from bieri-claude ──
Copy-Item "$github\bieri-claude\tools\package.sh"       "package.sh"
Copy-Item "$github\bieri-claude\tools\sync-meta.sh"     "sync-meta.sh"
Copy-Item "$github\bieri-claude\tools\audit_skill.py"   "shared\audit_skill.py"
Copy-Item -Path "$github\bieri-claude\shared-skills\session-handover\*" `
          -Destination "shared\session-handover\" -Recurse -Force
Copy-Item -Path "$github\bieri-claude\architecture\*" `
          -Destination "shared\architecture\" -Recurse -Force

# ── Extract skill source from each .skill file ──
# .skill files are zips — extract directly into skills\
# (each produces a subfolder like skills\course-compose-slides\)
$skills = @(
    "course-news-hooks",
    "course-build-kb",
    "course-video-scripts",
    "course-compose-slides",
    "course-assess-from-kb",
    "course-skill-builder"
)

foreach ($skill in $skills) {
    # Rename .skill → .zip, extract, remove .zip copy
    $skillFile = "$downloads\$skill.skill"
    $zipFile   = "$downloads\$skill.zip"
    Copy-Item $skillFile $zipFile -Force
    Expand-Archive -Path $zipFile -DestinationPath "skills\" -Force
    Remove-Item $zipFile -Force
    Write-Host "  extracted: $skill" -ForegroundColor Cyan
}

# ── Add dist\.gitkeep so the dist/ folder is tracked ──
New-Item -ItemType File -Path "dist\.gitkeep" -Force | Out-Null

# ── Commit and push ──
git add -A
git commit -m "init: bieri-teaching — 6 course: skills, build_kb.py, shared from bieri-claude"
git push -u origin main

Write-Host "bieri-teaching done." -ForegroundColor Green



# ============================================================
# REPO 3: bieri-research  (empty skeleton)
# ============================================================

cd $github
git clone https://github.com/david-bieri/bieri-research.git
cd bieri-research

# Create folder structure
New-Item -ItemType Directory -Path `
    skills, scripts, manifests, dist, `
    "shared\session-handover", "shared\architecture" -Force | Out-Null

# ── Root files ──
Copy-Item "$downloads\README_bieri_research.md"  "README.md"
Copy-Item "$downloads\gitignore_template.txt" ".gitignore"   # same .gitignore
Copy-Item "$downloads\BIERI_CLAUDE.md"           "BIERI_CLAUDE.md"

# ── Manifests ──
Copy-Item "$downloads\RESEARCH_MANIFEST.md"      "manifests\RESEARCH_MANIFEST.md"

# ── Sync shared tools from bieri-claude ──
Copy-Item "$github\bieri-claude\tools\package.sh"       "package.sh"
Copy-Item "$github\bieri-claude\tools\sync-meta.sh"     "sync-meta.sh"
Copy-Item "$github\bieri-claude\tools\audit_skill.py"   "shared\audit_skill.py"
Copy-Item -Path "$github\bieri-claude\shared-skills\session-handover\*" `
          -Destination "shared\session-handover\" -Recurse -Force
Copy-Item -Path "$github\bieri-claude\architecture\*" `
          -Destination "shared\architecture\" -Recurse -Force

# ── Placeholder files to track empty folders ──
New-Item -ItemType File -Path "skills\.gitkeep"   -Force | Out-Null
New-Item -ItemType File -Path "scripts\.gitkeep"  -Force | Out-Null
New-Item -ItemType File -Path "dist\.gitkeep"     -Force | Out-Null

# ── Commit and push ──
git add -A
git commit -m "init: bieri-research — skeleton with shared tools from bieri-claude"
git push -u origin main

Write-Host "bieri-research done." -ForegroundColor Green



# ============================================================
# REPO 4: bieri-admin
# ============================================================

cd $github
git clone https://github.com/david-bieri/bieri-admin.git
cd bieri-admin

# Create folder structure
New-Item -ItemType Directory -Path `
    "projects\agw", skills, scripts, manifests, dist, `
    "shared\session-handover", "shared\architecture" -Force | Out-Null

# ── Root files ──
Copy-Item "$downloads\README_bieri_admin.md"     "README.md"
Copy-Item "$downloads\gitignore_template.txt" ".gitignore"   # same .gitignore
Copy-Item "$downloads\BIERI_CLAUDE.md"           "BIERI_CLAUDE.md"

# ── Manifests ──
Copy-Item "$downloads\ADMIN_MANIFEST.md"         "manifests\ADMIN_MANIFEST.md"

# ── AGW project session notes (from your AGW Claude project) ──
# Copy your current AGW_SESSION_NOTES.md into projects\agw\
# (download it from your AGW Claude Project knowledge first)
# Copy-Item "$downloads\AGW_SESSION_NOTES.md" "projects\agw\AGW_SESSION_NOTES.md"
Write-Host "  NOTE: Copy AGW_SESSION_NOTES.md from your AGW Claude Project into projects\agw\" -ForegroundColor Yellow

# ── Sync shared tools from bieri-claude ──
Copy-Item "$github\bieri-claude\tools\package.sh"       "package.sh"
Copy-Item "$github\bieri-claude\tools\sync-meta.sh"     "sync-meta.sh"
Copy-Item "$github\bieri-claude\tools\audit_skill.py"   "shared\audit_skill.py"
Copy-Item -Path "$github\bieri-claude\shared-skills\session-handover\*" `
          -Destination "shared\session-handover\" -Recurse -Force
Copy-Item -Path "$github\bieri-claude\architecture\*" `
          -Destination "shared\architecture\" -Recurse -Force

# ── Placeholder files ──
New-Item -ItemType File -Path "skills\.gitkeep"   -Force | Out-Null
New-Item -ItemType File -Path "scripts\.gitkeep"  -Force | Out-Null
New-Item -ItemType File -Path "dist\.gitkeep"     -Force | Out-Null

# ── Commit and push ──
git add -A
git commit -m "init: bieri-admin — skeleton with AGW project, shared from bieri-claude"
git push -u origin main

Write-Host "bieri-admin done." -ForegroundColor Green



# ============================================================
# DONE — verify all four repos
# ============================================================

Write-Host ""
Write-Host "All repos initialised:" -ForegroundColor Green
Write-Host "  https://github.com/david-bieri/bieri-claude"
Write-Host "  https://github.com/david-bieri/bieri-teaching"
Write-Host "  https://github.com/david-bieri/bieri-research"
Write-Host "  https://github.com/david-bieri/bieri-admin"
Write-Host ""
Write-Host "Next: install skills via Claude Desktop → Cowork → Customize → Skills"
