# admin:family-hub

Build and maintain a full-stack family administration web app: shared calendar with recurrence, category management, email inbox scanning, vaccination tracking, pet management, and shareable read-only calendar links.

---

## When to invoke

Trigger on: "build the family hub", "add a feature to the family app", "debug the inbox pipeline", "set up the vaccine tracker", "add a new category", "generate a shareable calendar link", any request to extend or operate the household management portal.

This skill integrates: `admin:gmail-scanner`, `admin:tag-parser`, `admin:cron-agent`, `webdev:supabase-app`, `webdev:vite-express`, `webdev:deploy-render`, `webdev:platform-migration`.

---

## System overview

```
Frontend (React + Vite + Tailwind v3)
  ├── Dashboard      — upcoming events, all categories
  ├── Calendar       — monthly/weekly, color-coded by member
  ├── Categories     — CRUD with color assignment
  ├── Inbox          — pending email imports, approve/reject
  ├── Medical        — appointments + vaccine tracker per person
  ├── Pets           — profiles, vet, vaccines, medications, grooming
  ├── Sports         — practice schedules, game results
  └── Payments       — due dates, amounts, status

Backend (Express + Node.js)
  ├── /api/events         — CRUD + recurrence expansion
  ├── /api/categories     — CRUD (built-ins protected from delete)
  ├── /api/inbox/scan     — receive email items from scanner
  ├── /api/inbox/pending  — review queue for extracted items
  ├── /api/vaccines       — per-person vaccine records
  ├── /api/pets           — pet profiles + sub-resources
  └── /api/share          — generate/validate share tokens

Database (Supabase — 14 tables)
  events, vaccines, medical_appointments, sports, registrations,
  payments, categories, share_tokens, pending_imports,
  pets, pet_vet_appointments, pet_medications, pet_grooming, pet_vaccines
```

---

## Workflow

### Adding a new feature

1. Identify which table(s) are affected — check `references/migration.sql`
2. Add migration SQL if schema changes needed; run via Supabase SQL editor
3. Add/update Express route in `server/routes/`
4. Add/update React component in `client/src/`
5. Wire into sidebar nav and calendar view if it produces events
6. Test: build → start server → verify in browser → check `/api/health`

### Running the email pipeline manually

1. Follow `admin:gmail-scanner` steps 1–5
2. Extracted items appear in Inbox UI as `pending` status
3. Review and approve → items move to `events` table

### Generating a shareable calendar link

```typescript
// POST /api/share
const token = nanoid(32); // nanoid v3 — do NOT upgrade to v4 (ESM-only)
await supabase.from('share_tokens').insert({ token, label: 'Family Calendar' });
// Returns: { url: `/shared/${token}` }
```

Route `/shared/:token` renders full calendar, no login required.

---

## Configuration

### Family members

```typescript
const FAMILY_MEMBERS = [
  { name: 'Cole',       color: '#3b82f6', birthdate: '2012-06-29' },
  { name: 'Greta',      color: '#8b5cf6', birthdate: '2013-09-25' },
  { name: 'Airlie',     color: '#22c55e', birthdate: '2015-03-09' },
  { name: 'Clara',      color: '#f59e0b', birthdate: '2016-08-23' },
  { name: 'Heidi',      color: '#ec4899', birthdate: '2023-03-09' },
  { name: 'Daisy',      color: '#14b8a6', birthdate: '2025-01-28' },
];
```

### Pets

```typescript
const PETS = [
  { name: 'Otis',       species: 'dog', breed: 'Bernese Mountain Dog', color: '#78350f' },
  { name: 'Athena',     species: 'cat', breed: 'Russian Blue',          color: '#64748b' },
  { name: 'Persephone', species: 'cat', breed: 'Black Bombay',          color: '#1e1b4b' },
];
```

### Built-in categories (non-deletable)

```typescript
const BUILTIN_CATEGORIES = ['school','sports','medical','camp','family','payment','other'];
// 'pets' is seeded but deletable
```

### Recurrence

Supported: `none` | `daily` | `weekly`. Store `recurrence_end_date` as ISO date (null = indefinite). Expand recurring events client-side when rendering the calendar.

### Vaccine status values

`completed` | `scheduled` | `overdue` | `not_required` | `declined`

### Email tag syntax

```
#TAG @Name1 @Name2 Subject text
```
See `admin:tag-parser` for full tag registry and parsing logic.

---

## Critical technical constraints

| Item | Constraint |
|------|-----------|
| nanoid | v3 only — v4 is ESM-only, breaks the build |
| Tailwind | v3 only — v4 breaks `@tailwind` directives |
| Auth URL param | `?t=BASE64_ENCODED_PASSWORD` for direct access |
| Cron | `0 11 * * *` UTC = 7 AM EDT |
| POST target | Always `http://localhost:5000` (never proxy URL) |
| Build output | `dist/public/` (frontend) + `dist/index.cjs` (server) |

---

## Reference files

- `references/migration.sql` — full 14-table schema with RLS and seed data
- `assets/.env.example` — all environment variables

---

## QA checklist

- [ ] `/api/health` returns 200
- [ ] Auth flow works (password + `?t=` param)
- [ ] All 8 sidebar modules load without error
- [ ] Calendar renders events color-coded by family member
- [ ] Recurring events expand correctly in calendar view
- [ ] Inbox: approve flow moves item from `pending_imports` to `events`
- [ ] Vaccines: status badge colors correct for all 5 states
- [ ] Share link opens without login and shows full calendar
- [ ] Email scan: `#TAG @Name` subjects classified correctly
