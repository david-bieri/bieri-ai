# bieri-ai — Contract Normalization Plan

**Status:** PROPOSAL — for review. No repository files have been edited yet.
**Author:** Claude (audit + plan), pending David's approval to execute.
**Scope:** Clean the skill "contract" so the library is consistently identified,
authored, and wrapped — the precondition for stackable, recombinable skills.

---

## 0. Decisions locked (David, this session)

1. **Identity form:** directories stay **hyphenated**; in-skill identity is **colon-namespaced**.
2. **Namespace set:** `admin:`, `teaching:`, `research:`, `webdev:`, and **`home:` reserved** (pillar exists, no skills yet). Universal infrastructure stays **bare** (`session-handover`).
3. **`web-release-workflow` reclassified** to `webdev:release-workflow`.
4. **Template** fixed to drop YAML frontmatter (matches CONTRIBUTING §3).
5. **Wrapped artifacts** live only in git-ignored `dist/`; never committed beside source.
6. **The six paired reconciliations** are owned by **Claude** (this plan).
7. **The two orphans** (`webdev-messaging-inapp-sms`, `webdev-node-build-pitfalls`) are owned by **Perplexity** (out of scope here).

---

## 1. The canonical contract (target state)

A skill is **one source of truth** (`skills/<dir>/skill.md`) plus optional
`references/` and `scripts/`. Everything else is generated.

| Rule | Statement |
|------|-----------|
| **Directory** | `<namespace>-<name>` (hyphenated), e.g. `teaching-news-hooks`. |
| **Identity**  | `<namespace>:<name>` (colon), e.g. `teaching:news-hooks`. Appears as the `skill.md` H1 **and** is emitted by the adapter as `name:`. |
| **Namespaces** | `admin:`, `teaching:`, `research:`, `webdev:`, `home:`. Universal infra = bare name, no namespace. |
| **Source frontmatter** | **None.** `skill.md` is pure Markdown. (CONTRIBUTING §3.) |
| **Authored metadata** | `description`, `version`, `depends_on`, `used_by` live in a `metadata.yaml` sidecar (see §6, decision pending). |
| **Wrapped artifact** | Generated into `dist/claude/` (git-ignored). Never committed in `skills/`. |
| **Manifest** | Each domain's `SKILLS_MANIFEST.md` is the slow-layer source of truth; README inventory mirrors it. |

---

## 2. Root cause of the identity drift — the adapter

`adapters/claude/wrap_skill.py :: infer_metadata()` derives the deployed `name`
from the directory prefix, with hardcoded mappings that are the actual source of
the drift:

```
teaching-*  -> "course:" + rest      # re-injects the OLD namespace
webdev-*    -> dir name as-is         # hyphenated, never colon
else        -> dir name as-is         # admin-cron-agent, not admin:cron-agent
```

**Consequence:** editing the H1 inside any `skill.md` is cosmetic — the adapter
overwrites identity at wrap time. Issue #1 is therefore fixed **in the adapter
first**, then mirrored in the H1s for human readability and to stop the two from
disagreeing again.

Two further defects in the same function:

- **Description is scraped**, not authored: it takes the first paragraph after the
  H1, truncated to 200 chars. For contract-conformant skills (H1 immediately
  followed by `## When to invoke`) the scrape returns empty and falls back to
  `"Skill: <dir>"` — a non-functional trigger string. Triggering quality depends
  on this field, so this silently degrades every such skill.
- **`version` / `depends_on` / `used_by` are dropped** (hardcoded `1.0.0`, empty
  lists) unless a `metadata.yaml` sidecar is present — and none exist. The
  composition graph that makes skills recombinable never reaches the artifact.

---

## 3. Workstream A — Adapter rewrite (mechanism for issue #1)

Edit `adapters/claude/wrap_skill.py`:

1. **Name mapping** — replace the hardcoded branch with prefix-driven colon
   namespacing:

   ```python
   NAMESPACES = {"admin", "teaching", "research", "webdev", "home"}
   prefix, _, rest = skill_dir.name.partition("-")
   if prefix in NAMESPACES and rest:
       meta["name"] = f"{prefix}:{rest}"
   else:
       meta["name"] = skill_dir.name   # bare universal, e.g. session-handover
   ```

2. **ZIP folder name** — stop mashing colons out (`coursenews-hooks`). Use the
   hyphenated directory name for the ZIP folder and `.skill` filename, while the
   frontmatter `name:` keeps the colon:

   ```python
   zip_folder_name = skill_dir.name   # teaching-news-hooks/ ; teaching-news-hooks.skill
   ```

3. **Description / version / graph** — see §6 (pending decision). The name and
   ZIP-folder fixes are unblocked and can ship immediately.

**Validation:** after the rewrite, dry-run-wrap every skill and confirm the
emitted `name:` equals the canonical identity in the table below.

---

## 4. Workstream B — In-file identity normalization

Align each `skill.md` H1 (and any in-body self-reference) to the canonical
identity, so source and artifact agree. Directories unchanged.

| Directory | Current H1 | → Canonical identity |
|---|---|---|
| teaching-assess-from-kb | `course:assess-from-kb` | `teaching:assess-from-kb` |
| teaching-build-kb | `course:build-kb` | `teaching:build-kb` |
| teaching-compose-slides | `course:compose-slides` | `teaching:compose-slides` |
| teaching-news-hooks | `course:news-hooks` | `teaching:news-hooks` |
| teaching-skill-builder | `course:skill-builder` | `teaching:skill-builder` |
| teaching-video-scripts | `course:video-scripts` | `teaching:video-scripts` |
| webdev-contact-protocol-links | "Contact Protocol Links" | `webdev:contact-protocol-links` |
| webdev-cross-browser-smoke-test | "Systematic Smoke Testing" | `webdev:cross-browser-smoke-test` |
| webdev-d3-analytics-modules | "D3 Analytics Modules" | `webdev:d3-analytics-modules` |
| webdev-json-data-enrichment | "JSON Data Enrichment" | `webdev:json-data-enrichment` |
| webdev-latex-pdf-guide | "LaTeX PDF Guide & Web Delivery" | `webdev:latex-pdf-guide` |
| webdev-static-site-i18n | "Static Site i18n & Management" | `webdev:static-site-i18n` |
| web-release-workflow → **rename dir** to `webdev-release-workflow` | "Web Release Workflow" | `webdev:release-workflow` |

Already canonical (no edit): `admin:cron-agent`, `admin:family-hub`,
`admin:gmail-scanner`, `admin:tag-parser`, `webdev:deploy-render`,
`webdev:platform-migration`, `webdev:supabase-app`, `webdev:vite-express`,
`session-handover`.

**Note on the reclassification:** `web-release-workflow` is renamed to
`webdev-release-workflow` so the adapter prefix rule produces `webdev:release-workflow`
automatically. Update its references in the README and any manifest.

---

## 5. Workstream C — Template fix

`templates/skill_template.md` currently leads with an 11-line YAML frontmatter
block, contradicting CONTRIBUTING §3 and every actual source file. Fix:

- Delete the frontmatter block; the file starts at `# {namespace}:{skill-name}`.
- Add one line at top: `<!-- No YAML frontmatter — adapters add it (CONTRIBUTING §3). Metadata lives in metadata.yaml. -->`
- Keep the body sections (`When to invoke`, `Workflow`, `Output format`, `QA checklist`).

---

## 6. Workstream D — Artifact hygiene + the six reconciliations

`.gitignore` already excludes `dist/`, so the only violations are committed
`SKILL.md` files sitting inside `skills/<dir>/`. These are **not** stale adapter
output — they are independently authored (Perplexity-style) variants, several of
which are **ahead** of the source. Deleting them blindly destroys real content.

**Reconciliation principle:** *source skeleton + wrapped flesh.* The bieri-ai
contract structure is canonical (`## When to invoke`, `## Workflow`, `## QA
checklist`, terse imperative voice, **no frontmatter**). The wrapped variants use
a different convention (`## When to Use This Skill`, `## Step-by-Step
Instructions`, verbose "Load this skill when:" bullets, embedded frontmatter with
sometimes-wrong `domain:`) — that convention is discarded; only the substantive
technical content they add is merged in, plus any hand-authored description (which
becomes the sidecar `description`). All wrapped frontmatter is discarded.

| Skill | Pattern | Preserve from source | Merge in from wrapped |
|---|---|---|---|
| **admin-cron-agent** | two-way | `## QA checklist`, `## Migration note`, contract headings | `## Hosted App Pattern (Render/Railway/Fly.io)`; expanded Single-Invocation / Token-Isolation detail. (Wrapped `domain: universal` is wrong → discard; it's `admin`.) |
| **admin-family-hub** | clean superset (wrapped v1.2, no source-unique sections) | contract structure | Dashboard member tiles, Messaging module, Nav badge system, Architecture, Backend routes, Frontend unread-badge, Twilio setup |
| **admin-gmail-scanner** | two-way | `## QA checklist`, contract headings | `## Cron Schedule`, `## Notification Format`, expanded step detail |
| **webdev-deploy-render** | two-way (wrapped much richer) | `## QA checklist`, contract headings, Render-vs-sandbox-cron note | Auto-Deploy from GitHub, "Diagnosing Exited with status 1", `render.yaml` with `nodeVersion`, Cron Endpoint/Script, expanded setup steps |
| **webdev-supabase-app** | inline enrichment (same sections, richer within) | structure | v1.1 additions: Perplexity-Supabase-connector migration pattern, idempotent SQL, dual id-column (nanoid/text vs uuid) patterns |
| **webdev-vite-express** | two-way (wrapped much richer) | `## QA checklist`, contract headings | Tailwind v3 setup (incl. "never install `@tailwindcss/vite`", plugins in `dependencies`), Docker, Build-Script-and-tsx, Node-version, config file examples |

After each merge: confirm identity (§4), then **delete** the in-place `SKILL.md`.
Re-wrapping (§3) regenerates it into `dist/claude/`.

---

## 7. Workstream E — README / manifest / architecture-doc sync

- **README "Skills Inventory":** stale. WebDev table lists 6 of ~12; Admin's 4
  skills absent; Universal lists `web-release-workflow` (now `webdev:`). Rebuild
  all inventory tables from the actual roster.
- **Domain manifests:** ensure each `SKILLS_MANIFEST.md` Installed-Skills table
  matches the skills in that namespace and uses colon identities; append an Update
  Log entry noting the normalization. (`research` manifest stays empty — greenfield.)
- **`architecture/BIERI_AI.md` "Skill Namespaces":** currently lists `course:*`
  for Teaching. Update to `teaching:*`, add `home:*`, and state that universal
  skills are bare.

---

## 8. Flagged decisions (need David's call before execution)

These are implied by the contract but your four issues didn't settle them:

- **D1 — Description source.** Adopt `metadata.yaml` sidecars carrying an authored
  `description` (the ≤200-char "Use for X, Y, Z" trigger), so triggering stops
  depending on a broken scrape? (Recommended.) Alternative: designate the first
  post-H1 paragraph as the canonical description by convention and write it
  deliberately in every skill.
- **D2 — Version + graph propagation.** Same sidecar carries `version`,
  `depends_on`, `used_by` so the composition graph survives wrapping? (Recommended —
  this is what makes stackability real at the artifact level.)
- **D3 — ZIP-folder naming.** Confirm switching the ZIP folder / `.skill` filename
  to the hyphenated dir name (`teaching-news-hooks.skill`) instead of the
  colon-stripped mash (`coursenews-hooks.skill`).

D1 and D2 point at the same `metadata.yaml` sidecar; adopting it resolves both and
makes the adapter's metadata handling deterministic instead of inferred.

---

## 9. Sequencing

1. **Template fix** (C) — cheap; stops new skills entering drifted.
2. **Adapter rewrite** (A, name + ZIP-folder) — the mechanism for #1.
3. **In-file identity** (B) — including the `web-release-workflow` dir rename.
4. **Six reconciliations** (D) — merge, normalize identity, delete in-place `SKILL.md`.
5. **Sidecars** (D1/D2) — if approved.
6. **Docs sync** (E) — last; reflects final state.
7. **Verification** (§10).

---

## 10. Verification checklist

- [ ] `infer_metadata` emits the canonical colon identity for every skill (dry-run wrap, diff against §4 table).
- [ ] No `skills/*/SKILL.md` remain (only `skill.md` + `references/` + `scripts/`).
- [ ] No `skill.md` contains YAML frontmatter.
- [ ] Every `skill.md` H1 matches its canonical identity.
- [ ] `web-release-workflow` directory renamed; references updated.
- [ ] README inventory, domain manifests, and `BIERI_AI.md` namespaces match the actual roster.
- [ ] (If D1/D2 approved) every skill has a `metadata.yaml`; wrapped artifacts carry authored description + version + graph.
- [ ] `audit_skill.py` passes on every wrapped artifact.

---

## 11. Out of scope (dependencies)

- **Orphans** `webdev-messaging-inapp-sms`, `webdev-node-build-pitfalls`: Perplexity
  reconstructs platform-agnostic `skill.md`. This plan reserves their identities
  (`webdev:messaging-inapp-sms`, `webdev:node-build-pitfalls`) and will fold them
  into the README/manifest sync once their source exists.
- **`audit_skill.py` rules:** assumed current. If the description/identity rules
  change as a result of D1–D3, update the auditor to match.
