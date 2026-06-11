# HOME Session Notes — Bieri Family Hub

**Last session:** 2026-06-10
**Topic:** Built 8-skill bieri-ai suite; integrated into repo with proper naming conventions
**Project:** Bieri Family Hub
**Horizon:** Migration to Render (when ready to move off Perplexity sandbox)

---

## Project configuration

**Prefix:** FAM
**Pillar:** HOME (admin: skills)
**Registry:** `domains/home/SKILLS_MANIFEST.md`
**Dispatch:**
  → GitHub `david-bieri/bieri-family-hub` (app source)
  → GitHub `david-bieri/bieri-ai` (skill library)
  → Perplexity Computer (runtime + cron)
**Horizon:** Render migration when Perplexity cron proves insufficient

---

## 1. Completed this session

- ✓ Built 8-skill suite: `admin-cron-agent`, `admin-gmail-scanner`, `admin-tag-parser`, `admin-family-hub`, `webdev-supabase-app`, `webdev-vite-express`, `webdev-deploy-render`, `webdev-platform-migration`
- ✓ All skills saved to Perplexity user library (validated 8/8)
- ✓ Skills integrated into `bieri-ai` repo with correct naming conventions (no frontmatter in `skill.md`)
- ✓ `domains/admin/SKILLS_MANIFEST.md` updated (was empty)
- ✓ `domains/webdev/SKILLS_MANIFEST.md` updated (4 new skills added)
- ✓ `domains/home/` initialized (README, SKILLS_MANIFEST, SESSION_NOTES)

---

## 2. Pending dispatch

**[GitHub: bieri-ai]**
- All 8 skill directories + domain manifest updates — ready to push

---

## 3. Decisions made this session

**Skills use repo naming convention** — `admin-cron-agent` not `cron-agent`; no YAML frontmatter in `skill.md` per `CONTRIBUTING.md` rule.

**Family hub lives in `admin:` namespace, surfaces in `home:` domain** — the distinction is: `admin:` = technical skill implementation; `home:` = domain context and session state.

**8 skills are platform-agnostic** — they work for any multi-member household app, not just the Bieri family hub. The Bieri-specific config (names, colors, credentials) lives in session notes and the app's `.env`, not in the skill.md files.

---

## 4. Latent issues

- `family-inbox-scanner` skill in Perplexity library is superseded by `admin-gmail-scanner` + `admin-tag-parser` — consider deprecating
- `webdev-supabase-app/references/migration.sql` is the Family Hub schema; a more generic example would be preferable for the general skill

---

## 5. Open questions

- When to trigger Render migration? (app is stable; trigger = needing reliable cron without agent session)
- Should `admin-inbound-webhook` (SendGrid) replace Gmail polling as next step?

---

## 6. Suggested next session

"Read `HOME_SESSION_NOTES.md`, then stress-test the family hub by forwarding 10+ emails across all `#TAG` categories and verifying extraction accuracy in the Inbox UI."
