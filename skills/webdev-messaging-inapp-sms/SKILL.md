---
name: webdev-messaging-inapp-sms
description: "Add a unified messaging feed to a Vite+Express web app. In-app posts and inbound SMS via Twilio, with a nav badge that tracks unread messages via localStorage. Use when building a message board, family/team inbox, or any app that needs to receive SMS alongside in-app posts. Covers Supabase schema, backend routes, TwiML response pattern, localStorage unread tracking, and Twilio setup."
version: "1.0"
---

# webdev:messaging-inapp-sms
_v1.0_

Add a unified messaging feed to a web app: in-app posts and inbound SMS via Twilio, with a nav badge that tracks unread messages via localStorage.

---

## When to invoke

Trigger on: "add a message board", "add in-app messaging", "receive SMS in the app", "Twilio inbound webhook", "unread message badge", "unified chat feed", or any request to build a messaging or notifications feed in a Vite+Express app.

---

## Architecture

One `messages` table unifies both channels. `channel='app'` for in-app posts, `channel='sms'` for Twilio inbound. No third-party service is needed for the in-app channel; Twilio is only required for SMS.

```
User (browser)  →  POST /api/messages  →  Supabase messages table
Mobile phone    →  SMS to Twilio number  →  POST /api/sms/inbound  →  Supabase messages table
Messages page   →  GET /api/messages   →  unified feed, newest at bottom
Nav badge       →  GET /api/messages/count?since=ISO  →  unread count
```

---

## Database

### messages table

```sql
CREATE TABLE messages (
  id           TEXT PRIMARY KEY,
  channel      TEXT NOT NULL DEFAULT 'app',   -- 'app' | 'sms'
  author       TEXT NOT NULL,
  body         TEXT NOT NULL,
  phone_from   TEXT,                           -- raw E.164 for SMS rows only
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX messages_created_at_idx ON messages (created_at DESC);
```

### phone_contacts table (optional)

Maps E.164 phone numbers to display names. If no mapping exists, raw phone number is shown as author.

```sql
CREATE TABLE phone_contacts (
  id    TEXT PRIMARY KEY,
  phone TEXT NOT NULL UNIQUE,   -- E.164: +15405551234
  name  TEXT NOT NULL
);
```

---

## Backend routes

Add as a standalone registered function to keep routes.ts modular:

```typescript
export function registerMessageRoutes(app: Express) {

  // GET /api/messages
  // Returns latest 100 messages, newest first
  app.get("/api/messages", async (_req, res) => {
    const { data, error } = await supabase
      .from("messages")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(100);
    if (error) return res.status(500).json({ error: error.message });
    res.json(data || []);
  });

  // GET /api/messages/count?since=ISO
  // Counts messages newer than the given timestamp — used for nav badge
  app.get("/api/messages/count", async (req, res) => {
    const since = (req.query.since as string) || new Date(0).toISOString();
    const { count, error } = await supabase
      .from("messages")
      .select("*", { count: "exact", head: true })
      .gt("created_at", since);
    if (error) return res.status(500).json({ error: error.message });
    res.json({ count: count || 0 });
  });

  // POST /api/messages
  // Body: { author: string, body: string }
  app.post("/api/messages", async (req, res) => {
    const { author, body } = req.body;
    if (!author?.trim() || !body?.trim())
      return res.status(400).json({ error: "author and body are required" });
    const { data, error } = await supabase
      .from("messages")
      .insert({ id: nanoid(), channel: "app", author: author.trim(), body: body.trim() })
      .select()
      .single();
    if (error) return res.status(500).json({ error: error.message });
    res.json(data);
  });

  // POST /api/sms/inbound
  // Twilio webhook — content-type: application/x-www-form-urlencoded
  // Fields: From (E.164), Body (message text), plus many others Twilio sends
  app.post("/api/sms/inbound", async (req, res) => {
    const from: string = req.body.From || "";
    const body: string = req.body.Body || "";

    if (!from || !body) {
      // Always respond with valid TwiML — Twilio retries on non-2xx or invalid XML
      res.set("Content-Type", "text/xml");
      return res.send("<?xml version='1.0' encoding='UTF-8'?><Response></Response>");
    }

    // Resolve display name, fall back to raw phone number
    const { data: contact } = await supabase
      .from("phone_contacts")
      .select("name")
      .eq("phone", from)
      .single();
    const author = contact?.name || from;

    await supabase.from("messages").insert({
      id: nanoid(),
      channel: "sms",
      author,
      body: body.trim(),
      phone_from: from,
    });

    // Empty TwiML response — no auto-reply
    res.set("Content-Type", "text/xml");
    res.send("<?xml version='1.0' encoding='UTF-8'?><Response></Response>");
  });
}
```

Register in `server/index.ts`:
```typescript
import { registerMessageRoutes } from "./routes";
registerMessageRoutes(app);
```

---

## Frontend: Messages page

Key patterns:

### Unread tracking via localStorage

```typescript
const LS_KEY = "appName_lastReadMessages";

export function markMessagesRead() {
  localStorage.setItem(LS_KEY, new Date().toISOString());
}

// On page mount — clears the nav badge
useEffect(() => {
  markMessagesRead();
  queryClient.invalidateQueries({ queryKey: ["/api/messages/count"] });
}, [queryClient]);
```

### Author color (stable, no backend needed)

```typescript
const COLORS = ["bg-blue-500", "bg-purple-500", "bg-green-600", "bg-amber-500", "bg-rose-500", "bg-teal-600"];
function authorColor(author: string) {
  let h = 0;
  for (let i = 0; i < author.length; i++) h = (h * 31 + author.charCodeAt(i)) & 0xffffffff;
  return COLORS[Math.abs(h) % COLORS.length];
}
```

### Author name persistence

```typescript
const [author, setAuthor] = useState(() => localStorage.getItem("appName_author") || "");
// On successful send:
localStorage.setItem("appName_author", author.trim());
```

### Feed display order

API returns newest-first; reverse before rendering so newest appears at bottom (chat convention):
```typescript
const ordered = [...messages].reverse();
```

---

## Nav badge

In the Layout component, add a `useNavBadges()` hook:

```typescript
const { data: msgCountData } = useQuery({
  queryKey: ["/api/messages/count"],
  queryFn: async () => {
    const since = encodeURIComponent(
      localStorage.getItem("appName_lastReadMessages") || new Date(0).toISOString()
    );
    return (await apiRequest("GET", `/api/messages/count?since=${since}`)).json();
  },
  refetchInterval: 30_000,
});
// badgeCount = msgCountData?.count || 0
```

Nav entry:
```typescript
{ href: "/messages", label: "Messages", icon: MessageSquare, badgeKey: "messages" }
```

---

## Twilio setup

1. Create account at twilio.com → buy a US phone number (~$1.15/mo)
2. Set inbound webhook on the number:
   - URL: `https://your-app.onrender.com/api/sms/inbound`
   - Method: HTTP POST
3. No server-side env vars needed for inbound-only mode
4. (Optional) Add `TWILIO_AUTH_TOKEN` and validate `X-Twilio-Signature` header for production hardening
5. Add friendly names to `phone_contacts` table for known senders

### Express must parse URL-encoded bodies

Twilio sends `application/x-www-form-urlencoded`. Ensure this is registered before your routes:
```typescript
app.use(express.urlencoded({ extended: false }));
```

---

## Cold-start risk (Render free tier)

Twilio expects a response within ~15 seconds. Render free tier sleeps after 15 min of inactivity (cold start ~30s). Mitigation: use UptimeRobot or similar to ping `/api/health` every 5 minutes. Paid Render tier ($7/mo) eliminates this.

---

## QA checklist

- [ ] `messages` and `phone_contacts` tables exist in Supabase
- [ ] GET `/api/messages` returns array (empty OK)
- [ ] POST `/api/messages` with `{ author, body }` returns saved record
- [ ] POST `/api/sms/inbound` with `From=+1xxx&Body=hello` returns `<Response></Response>` XML
- [ ] Messages page: compose → send → message appears in feed
- [ ] Messages page: nav badge clears on visit
- [ ] Badge re-appears if a new message arrives after last visit
- [ ] Author color is stable (same name always same color)
- [ ] Author name persisted in localStorage between sessions
- [ ] `express.urlencoded({ extended: false })` registered before routes
