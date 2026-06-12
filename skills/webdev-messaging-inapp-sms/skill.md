# webdev:messaging-inapp-sms

Add a unified messaging feed to any web app: in-app posts and inbound SMS via Twilio, with a nav badge that tracks unread messages using a client-side timestamp.

---

## When to invoke

Trigger on: "add a message board", "add in-app messaging", "receive SMS in the app", "Twilio inbound webhook", "unread message badge", "unified chat feed", or any request to build a messaging or notifications feed in a Node.js/Express-backed app.

---

## Architecture

One `messages` table unifies both channels. `channel='app'` for in-app posts, `channel='sms'` for Twilio inbound. The in-app channel requires no third-party service. Twilio is only required if SMS intake is wanted.

```
Browser user    →  POST /api/messages            →  messages table (channel='app')
Mobile phone    →  SMS → Twilio → webhook POST   →  messages table (channel='sms')
Messages page   →  GET /api/messages             →  unified feed, newest at bottom
Nav badge       →  GET /api/messages/count?since →  count of messages since last visit
```

---

## Database schema

The schema uses standard SQL — compatible with PostgreSQL, SQLite, MySQL, or any Supabase project.

### messages

```sql
CREATE TABLE IF NOT EXISTS messages (
  id           TEXT PRIMARY KEY,          -- app-generated (e.g. nanoid, uuid, cuid)
  channel      TEXT NOT NULL DEFAULT 'app',   -- 'app' | 'sms'
  author       TEXT NOT NULL,
  body         TEXT NOT NULL,
  phone_from   TEXT,                      -- raw E.164 for SMS rows only
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS messages_created_at_idx ON messages (created_at DESC);
```

### phone_contacts (optional)

Maps E.164 phone numbers to display names. If no mapping exists, the raw number is shown as author.

```sql
CREATE TABLE IF NOT EXISTS phone_contacts (
  id    TEXT PRIMARY KEY,
  phone TEXT NOT NULL UNIQUE,   -- E.164: +15405551234
  name  TEXT NOT NULL
);
```

---

## Backend routes

### Dependencies

```bash
# No npm package needed for inbound-only Twilio — Twilio POSTs to your URL
# Only needed if validating Twilio signatures (recommended for production):
npm install twilio
```

The ID generator is your choice — any unique string works:
```typescript
// Options (pick one):
import { nanoid } from 'nanoid';          // v3 in CommonJS builds, v4+ in ESM
import { v4 as uuid } from 'uuid';
import { createId } from '@paralleldrive/cuid2';
```

### Route registration pattern

```typescript
// routes/messages.ts (or equivalent module)
import type { Express } from 'express';
import { db } from '../lib/db';  // your database client — Supabase, Prisma, Knex, etc.

export function registerMessageRoutes(app: Express) {

  // GET /api/messages
  // Returns latest 100 messages, newest first
  app.get('/api/messages', async (_req, res) => {
    try {
      const messages = await db.messages.findMany({ /* newest first, limit 100 */ });
      res.json(messages);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // GET /api/messages/count?since=ISO
  // Counts messages newer than the given ISO timestamp — used for the nav badge
  app.get('/api/messages/count', async (req, res) => {
    const since = (req.query.since as string) || new Date(0).toISOString();
    try {
      const count = await db.messages.count({ where: { created_at: { gt: since } } });
      res.json({ count });
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // POST /api/messages
  // Body: { author: string, body: string }
  app.post('/api/messages', async (req, res) => {
    const { author, body } = req.body;
    if (!author?.trim() || !body?.trim())
      return res.status(400).json({ error: 'author and body are required' });
    try {
      const msg = await db.messages.create({
        data: { id: generateId(), channel: 'app', author: author.trim(), body: body.trim() }
      });
      res.json(msg);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // POST /api/sms/inbound
  // Twilio webhook — content-type: application/x-www-form-urlencoded
  // Required fields: From (E.164 phone), Body (message text)
  // IMPORTANT: must respond with TwiML XML — Twilio retries on non-2xx or missing XML
  app.post('/api/sms/inbound', async (req, res) => {
    const from: string = req.body.From || '';
    const body: string = req.body.Body || '';

    const twimlEmpty = "<?xml version='1.0' encoding='UTF-8'?><Response></Response>";

    if (!from || !body) {
      res.set('Content-Type', 'text/xml');
      return res.send(twimlEmpty);
    }

    // Resolve display name from phone_contacts, fall back to raw number
    const contact = await db.phoneContacts.findFirst({ where: { phone: from } });
    const author = contact?.name || from;

    await db.messages.create({
      data: { id: generateId(), channel: 'sms', author, body: body.trim(), phone_from: from }
    });

    res.set('Content-Type', 'text/xml');
    res.send(twimlEmpty);
  });
}
```

### Express prerequisites

Both JSON and URL-encoded body parsers must be registered **before** these routes:

```typescript
app.use(express.json());
app.use(express.urlencoded({ extended: false }));  // required for Twilio webhook
```

---

## Frontend patterns

### Unread tracking via client-side timestamp

Store the last-read time in `localStorage`. No server-side session or auth required.

```typescript
const LS_LAST_READ_KEY = 'app_lastReadMessages';

function getLastRead(): string {
  return localStorage.getItem(LS_LAST_READ_KEY) || new Date(0).toISOString();
}

function markMessagesRead(): void {
  localStorage.setItem(LS_LAST_READ_KEY, new Date().toISOString());
}

// On Messages page mount — clears the badge immediately
useEffect(() => {
  markMessagesRead();
  queryClient.invalidateQueries({ queryKey: ['/api/messages/count'] });
}, [queryClient]);
```

Nav badge query:
```typescript
const { data } = useQuery({
  queryKey: ['/api/messages/count'],
  queryFn: async () => {
    const since = encodeURIComponent(getLastRead());
    return fetch(`/api/messages/count?since=${since}`).then(r => r.json());
  },
  refetchInterval: 30_000,
});
const unreadCount = data?.count || 0;
```

### Feed display order

The API returns newest-first for efficiency. Reverse client-side so newest appears at the bottom (chat convention):
```typescript
const ordered = [...messages].reverse();
```

### Author avatar color (stable hash, no CSS framework required)

Produces a consistent color per author name. Works with any styling approach — adapt hex values to match your design system.

```typescript
// Returns one of N hex colors, stable for a given author string
const AVATAR_COLORS = ['#3b82f6','#8b5cf6','#22c55e','#f59e0b','#ec4899','#14b8a6'];

function authorColor(author: string): string {
  let h = 0;
  for (let i = 0; i < author.length; i++)
    h = (h * 31 + author.charCodeAt(i)) & 0xffffffff;
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
}

// Usage (framework-agnostic inline style):
<div style={{ backgroundColor: authorColor(msg.author) }}>
  {msg.author.charAt(0).toUpperCase()}
</div>
```

### Author name persistence

Persist the author name so users don't have to re-enter it each session:
```typescript
const [author, setAuthor] = useState(
  () => localStorage.getItem('app_messageAuthor') || ''
);
// After successful send:
localStorage.setItem('app_messageAuthor', author.trim());
```

---

## Twilio setup

### One-time configuration

1. Create a Twilio account → buy a phone number in your country (~$1–2/mo)
2. In the number's Messaging settings, set the inbound webhook:
   - URL: `https://your-app-domain.com/api/sms/inbound`
   - Method: HTTP POST
3. No server-side env vars are needed for **inbound-only** mode — Twilio simply POSTs to your URL
4. For production hardening (optional), validate the `X-Twilio-Signature` header using `TWILIO_AUTH_TOKEN`

### Add display names for known senders

Insert rows into `phone_contacts` to map phone numbers to friendly names:
```sql
INSERT INTO phone_contacts (id, phone, name) VALUES
  ('c1', '+15405551234', 'Alice'),
  ('c2', '+15405559876', 'Bob')
ON CONFLICT DO NOTHING;
```

---

## Cold-start considerations

Twilio expects an HTTP response within ~15 seconds. If your app is hosted on a free tier with automatic sleep (e.g. Render free, Fly.io free), an inbound SMS during a cold start may time out. Mitigations:
- Use a monitoring service (UptimeRobot, Better Uptime) to ping `/api/health` every 5 min
- Upgrade to a paid hosting tier (typically $7–10/mo) to avoid sleep entirely
- Use a paid Twilio messaging service with retry enabled — Twilio will retry failed webhooks

---

## QA checklist

- [ ] `messages` table exists with correct columns and index
- [ ] `express.json()` and `express.urlencoded()` registered before routes
- [ ] GET `/api/messages` returns array (empty OK on fresh DB)
- [ ] POST `/api/messages` with `{ author, body }` returns saved record
- [ ] POST `/api/sms/inbound` with `From=+1xxx&Body=hello` returns `<Response></Response>` XML with `Content-Type: text/xml`
- [ ] Messages page: type → send → message appears in feed
- [ ] Nav badge clears when Messages page is opened
- [ ] Badge reappears after a new message arrives
- [ ] Author color is stable across page reloads for the same name
- [ ] Author name survives page reload (localStorage persistence)
