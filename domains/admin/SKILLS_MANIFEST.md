# Admin Skills Manifest — Prof. David Bieri

*Skills for administrative and household management workflows. Runs on Claude and Perplexity Computer.*

---

## Installed Skills

| Skill | Version | Status | Updated |
|-------|---------|--------|---------|
| `admin-cron-agent` | 1.0.0 | Active | 2026-06-10 |
| `admin-gmail-scanner` | 1.0.0 | Active | 2026-06-10 |
| `admin-tag-parser` | 1.0.0 | Active | 2026-06-10 |
| `admin-family-hub` | 1.0.0 | Active | 2026-06-10 |

---

## Skill Dependency Map

```
admin-family-hub
  ├── admin-gmail-scanner
  │   └── admin-cron-agent
  ├── admin-tag-parser
  ├── webdev-supabase-app   (see webdev manifest)
  ├── webdev-vite-express   (see webdev manifest)
  ├── webdev-deploy-render  (see webdev manifest)
  └── webdev-platform-migration (see webdev manifest)
```

---

## Active Projects

| Project | Prefix | Session notes | Repo |
|---------|--------|--------------|------|
| Bieri Family Hub | FAM | `HOME_SESSION_NOTES.md` (in `domains/home/`) | [david-bieri/bieri-family-hub](https://github.com/david-bieri/bieri-family-hub) |

---

## Key Decisions

- **Email intake:** Dedicated Gmail `bieri.family.hub@gmail.com` — not personal inbox
- **Tag syntax:** `#TAG @Name1 @Name2 Subject` (not `[TAG]` bracket syntax)
- **Cron:** `0 11 * * *` UTC = 7 AM EDT — daily scan
- **Cron architecture:** Agent calls `search_email` directly → writes file → single bash invocation
- **Migration target:** Render (backend + cron) + Supabase (unchanged) + Twilio SendGrid inbound (~$1/mo)

---

## Candidate Skills

| Candidate | Domain | Trigger |
|-----------|--------|---------|
| `admin-inbound-webhook` | admin | Replace Gmail polling with SendGrid inbound parse |
| `admin-shared-calendar` | admin | Export family calendar to Google Calendar / iCal |

---

## Update Log

| Date | Action | Detail |
|------|--------|--------|
| 2026-06-10 | Added | `admin-cron-agent` v1.0.0 — single-invocation cron pattern |
| 2026-06-10 | Added | `admin-gmail-scanner` v1.0.0 — Gmail intake pipeline |
| 2026-06-10 | Added | `admin-tag-parser` v1.0.0 — `#TAG @Name` subject-line classifier |
| 2026-06-10 | Added | `admin-family-hub` v1.0.0 — full household management app |
