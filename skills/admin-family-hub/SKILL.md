# admin:family-hub
_v1.2 — adds messaging module, nav badges, clickable dashboard tiles_

Build and maintain a full-stack family administration web app: shared calendar with recurrence, category management, email inbox scanning, vaccination tracking, pet management, messaging, shareable read-only calendar links.

---

## When to invoke

Trigger on: "build the family hub", "add a feature to the family app", "debug the inbox pipeline", "set up the vaccine tracker", "add a new category", "generate a shareable calendar link", "add messaging to the app", any request to extend or operate the household management portal.

This skill integrates: `admin:gmail-scanner`, `admin:tag-parser`, `admin:cron-agent`, `webdev:supabase-app`, `webdev:vite-express`, `webdev:deploy-render`, `webdev:platform-migration`.

---

## System overview

```
Frontend (React + Vite + Tailwind v3)
  ├── Dashboard      — upcoming events, clickable member tiles, all categories
  ├── Family Calendar— monthly view, color-coded by member, child deep-link filter
  ├── Schedule       — agenda/list view with add/edit
  ├── Categories     — CRUD with color assignment
  ├── Inbox          — pending email imports, approve/reject
  ├── Medical        — appointments + vaccine tracker per person
  ├── Messages       — unified in-app + inbound SMS feed
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
  ├── /api/messages       — GET (feed), POST (in-app post), count?since=
  ├── /api/sms/inbound    — Twilio webhook for inbound SMS
  └── /api/share          — generate/validate share tokens

Database (Supabase — 16 tables)
  events, vaccines, medical_appointments, sports, registrations,
  payments, categories, share_tokens, pending_imports,
  pets, pet_vet_appointments, pet_medications, pet_grooming, pet_vaccines,
  messages, phone_contacts
```

---

## Workflow

### Adding a new feature

1. Read the relevant source files fully before writing anything
2. Identify which table(s) are affected — check `references/migration.sql`
3. Add migration SQL if schema changes needed; apply via Supabase connector tool `apply_migration`
4. Add/update Express route in `server/routes.ts` as an exported `registerXxxRoutes(app)` function
5. Register in `server/index.ts` alongside existing registrations
6. Add/update React component in `client/src/pages/`
7. Wire into sidebar nav (`Layout.tsx`) and add to `App.tsx` routes
8. Add badge key if the feature produces actionable counts
9. Build → push → Render auto-deploys

### Running the email pipeline manually

1. Follow `admin:gmail-scanner` steps 1–5
2. Extracted items appear in Inbox UI as `pending` status
3. Review and approve → items move to `events` table

### Generating a shareable calendar link

```typescript
// POST /api/share
const token = nanoid(32); // nanoid v3 — do NOT upgrade to v4 (ESM-only)
await supabase.from('share_tokens').insert({ token, label: 'Family Calendar' });
// Returns: { url: `/?share=${token}` }
```

Route checks `?share=` query param at app boot — renders SharedCalendar component without login.

---

## Dashboard: clickable member tiles

Both THE KIDS and THE PETS rows on the dashboard are clickable tiles.

**Kids → pre-filtered Family Calendar**
```tsx
<Link href={`/family-calendar?child=${child.id}`}>
```

FamilyCalendar reads the param on mount via `getHashChildParam()`:
```typescript
function getHashChildParam(): string | null {
  const hash = window.location.hash; // e.g. "#/family-calendar?child=cole"
  const qIndex = hash.indexOf("?");
  if (qIndex === -1) return null;
  return new URLSearchParams(hash.slice(qIndex + 1)).get("child");
}
// Used as useState initializer:
const [filterChildren, setFilterChildren] = useState<string[]>(() => {
  const c = getHashChildParam();
  return c ? [c] : [];
});
```

**Pets → Pets page**
```tsx
<Link href="/pets">
```

**Visual differentiation:**
- Kids: circular avatar (`rounded-full`) with letter initial and CSS color class
- Pets: rounded-square avatar (`rounded-lg`) with species emoji on inline hex color background

---

## Nav badge system

`useNavBadges()` hook in `Layout.tsx` drives all nav badges:

| Nav item | Badge source | Logic |
|---|---|---|
| Inbox | `/api/inbox/count` | Count of pending_imports |
| Payments | `/api/payments` | `status === "overdue"` count |
| Medical | `/api/appointments` | not completed + future date |
| Camps & Reg. | `/api/registrations` | deadline within 30 days, not confirmed/cancelled |
| Messages | `/api/messages/count?since=` | newer than `localStorage.familyHub_lastReadMessages` |

Badge clears on page visit. `refetchInterval`: Inbox/Messages = 30–60s; others = 5 min.

NAV array entry format:
```typescript
{ href: "/payments", label: "Payments", icon: CreditCard, badgeKey: "payments" }
```

---

## Messaging module

### Architecture

One unified `messages` table for both channels:

```sql
CREATE TABLE messages (
  id           TEXT PRIMARY KEY,
  channel      TEXT NOT NULL DEFAULT 'app',   -- 'app' | 'sms'
  author       TEXT NOT NULL,
  body         TEXT NOT NULL,
  phone_from   TEXT,                           -- raw E.164 for SMS rows
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Optional display-name resolution:
```sql
CREATE TABLE phone_contacts (
  id    TEXT PRIMARY KEY,
  phone TEXT NOT NULL UNIQUE,   -- E.164, e.g. +15405551234
  name  TEXT NOT NULL
);
```

### Backend routes

```typescript
export function registerMessageRoutes(app: Express) {
  // GET /api/messages — latest 100, newest first
  // GET /api/messages/count?since=ISO — unread count for badge
  // POST /api/messages — { author, body } → in-app post
  // POST /api/sms/inbound — Twilio x-www-form-urlencoded webhook
}
```

Twilio webhook pattern:
```typescript
app.post("/api/sms/inbound", async (req, res) => {
  const from: string = req.body.From || "";
  const body: string = req.body.Body || "";
  // Resolve author from phone_contacts or fall back to raw number
  const { data: contact } = await supabase
    .from("phone_contacts").select("name").eq("phone", from).single();
  const author = contact?.name || from;
  await supabase.from("messages").insert({ id: nanoid(), channel: "sms", author, body, phone_from: from });
  // Must respond with empty TwiML — Twilio expects XML
  res.set("Content-Type", "text/xml");
  res.send("<?xml version='1.0' encoding='UTF-8'?><Response></Response>");
});
```

### Frontend: unread badge via localStorage

```typescript
const LS_KEY = "familyHub_lastReadMessages";
export function markMessagesRead() {
  localStorage.setItem(LS_KEY, new Date().toISOString());
}
// On Messages page mount:
useEffect(() => {
  markMessagesRead();
  qc.invalidateQueries({ queryKey: ["/api/messages/count"] });
}, [qc]);
```

### Twilio setup (one-time)

1. Create Twilio account → buy US number (~$1.15/mo)
2. Set inbound webhook: `https://your-app.onrender.com/api/sms/inbound` (HTTP POST)
3. No env vars needed for inbound-only — Twilio POSTs to your URL
4. Add phone contacts to `phone_contacts` table for display-name resolution
5. (Optional hardening) Add `TWILIO_AUTH_TOKEN` for signature validation

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
| tailwind.config | Must be `.js` with `module.exports` (not `.ts`) — jiti v2 incompatibility |
| Auth URL param | `?t=BASE64_ENCODED_PASSWORD` for direct access |
| Cron | `0 11 * * *` UTC = 7 AM EDT |
| Env vars | Server reads `SUPABASE_URL \|\| VITE_SUPABASE_URL` (supports both naming conventions) |
| Build output | `dist/public/` (frontend) + `dist/index.cjs` (server) |
| Router | `<Router hook={useHashLocation}>` must wrap `<Layout>` — not nested inside it |
| Deep-link params | Hash query format: `#/route?param=value` — parse from `window.location.hash` |

---

## Reference files

- `references/migration.sql` — full 16-table schema with RLS and seed data
- `assets/.env.example` — all environment variables

---

## QA checklist

- [ ] `/api/health` returns 200
- [ ] Auth flow works (password + `?t=` param)
- [ ] All 10 sidebar modules load without error
- [ ] Dashboard kid tiles link to pre-filtered Family Calendar
- [ ] Dashboard pet tiles link to Pets page
- [ ] Nav badges show correct counts for all 5 badged items
- [ ] Messages page: in-app post appears in feed; badge clears on visit
- [ ] Inbound SMS: POST to `/api/sms/inbound` with Form/Body fields creates message
- [ ] Calendar renders events color-coded by family member
- [ ] Recurring events expand correctly in calendar view
- [ ] Inbox: approve flow moves item from `pending_imports` to `events`
- [ ] Vaccines: status badge colors correct for all 5 states
- [ ] Share link opens without login and shows full calendar
- [ ] Email scan: `#TAG @Name` subjects classified correctly
