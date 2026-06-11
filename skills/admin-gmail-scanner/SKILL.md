---
name: admin-gmail-scanner
description: "Scan a dedicated Gmail account for structured emails, extract calendar items and action items using subject-line tag fast-path or LLM fallback, deduplicate by gmail_id, and POST results to an app API endpoint. Use when building scheduled email intake pipelines, family/team inbox automation, or any system that converts forwarded emails into structured data. Pairs with cron-agent for scheduling and tag-parser for classification."
metadata:
  version: '1.0'
  domain: admin
  author: bieri-ai
---

# Gmail Scanner

## When to Use This Skill

Load this skill when:
- Building a scheduled pipeline to scan a Gmail inbox for actionable emails
- Setting up a dedicated intake address (e.g. `myapp@gmail.com`) for forwarded emails
- Extracting structured calendar items, deadlines, or payments from email content
- Integrating with a Supabase or REST backend via POST

## Architecture Overview

```
Gmail (dedicated inbox)
    ↓  [agent calls search_email directly]
Filtered email list
    ↓  [write to /tmp/emails_to_scan.json]
Single bash call
    ↓  [start server → POST each email → kill server]
/tmp/scan_results.json
    ↓  [agent reads + notifies]
In-app notification (if new items found)
```

**Key constraint:** The `gcal` connector's `search_email` tool must be called by the **agent**, not from inside a bash subprocess. Write results to file first; then a single bash call handles all server-side work.

## Step-by-Step Instructions

### Step 1 — Compute Lookback Window
```bash
python3 -c "
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y/%m/%d'))
"
```

### Step 2 — Search Gmail (agent call)
Call `search_email` on the `gcal` connector with these queries (substitute DATE from Step 1):

```json
{
  "queries": [
    "registration deadline",
    "camp registration",
    "payment due",
    "school newsletter",
    "appointment reminder",
    "practice schedule",
    "sports schedule",
    "permission slip",
    "field trip",
    "vaccine reminder",
    "doctor appointment",
    "summer program",
    "enrollment",
    "after:DATE (registration OR deadline OR payment OR appointment OR schedule)"
  ]
}
```

Response shape: `{ email_results: { emails: [...] } }`
Each email has: `email_id`, `subject`, `from_`, `date`, `snippet`, `body`

**Filter out:**
- Duplicate `email_id` (keep first)
- Emails from Google system addresses (`noreply@google.com`, `accounts.google.com`, security alerts)

### Step 3 — Write to File
Write filtered emails to `/tmp/emails_to_scan.json`:
```json
[
  {
    "gmail_id": "abc123",
    "subject": "#CAMP @Clara Registration deadline June 30",
    "from": "sender@example.com",
    "date": "2024-06-01",
    "snippet": "...",
    "body": "..."
  }
]
```

If no relevant emails, write: `[]`

### Step 4 — POST Emails to API

**If the app is hosted (Render, Railway, etc.)** — POST directly to the public URL. No server start needed:

```python
import json, urllib.request

API = "https://your-app.onrender.com/api/inbox/scan"  # public Render URL
emails = json.load(open("/tmp/emails_to_scan.json"))
results = []
total_extracted = 0

for email in emails:
    payload = json.dumps({
        "gmail_id": email.get("gmail_id") or email.get("email_id", ""),
        "subject":  email.get("subject", ""),
        "from":     email.get("from", "") or email.get("from_", ""),
        "date":     email.get("date", ""),
        "snippet":  (email.get("snippet") or "")[:500],
        "body":     (email.get("body") or "")[:3000],
    }).encode()
    try:
        req = urllib.request.Request(API, data=payload,
                                     headers={"Content-Type": "application/json"})
        # 60s timeout — Render free tier may need 30-60s to wake from sleep
        resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
    except Exception as e:
        resp = {"error": str(e)}
    # ... collect results
```

**If the app runs locally in the agent sandbox** — use the single-invocation shell script:

```bash
bash /path/to/scripts/post_emails.sh /tmp/emails_to_scan.json
```

See `scripts/post_emails.sh` for the full runner (build → start → POST → kill → write results).

### Step 5 — Read Results and Notify
```bash
cat /tmp/scan_results.json
```

Results shape:
```json
{
  "total_extracted": 2,
  "results": [
    {"subject": "#CAMP @Clara ...", "status": "extracted", "count": 1},
    {"subject": "Soccer schedule", "status": "skipped", "count": 0}
  ]
}
```

- `total_extracted > 0` → send in-app notification with bullet list of extracted subjects
- `total_extracted == 0` → end silently (no notification)

## Notification Format

```
Title: "Family Hub — 3 new inbox items to review"
Body:
• #CAMP @Clara — Registration deadline (1 item)
• #MED @Heidi — Vaccine reminder (1 item)
• #PAY @Cole — Soccer payment due (1 item)
```

## Dedicated Inbox Setup

Using a dedicated address (not personal Gmail) is strongly recommended:
1. Create `yourapp@gmail.com` (or use a subdomain alias)
2. Family/team members forward relevant emails to this address
3. Connect this account via OAuth (separate from personal Gmail)
4. Scanner reads only this inbox — no personal email exposure

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 0 emails returned | Wrong account connected | Verify connector points to intake Gmail |
| 403 on POST | Proxy URL used instead of localhost | Always use `http://localhost:PORT` |
| Duplicate items | `gmail_id` check missing | Deduplicate before writing to file |
| Token error in bash | `api_credentials` not set | Agent calls `search_email` directly |
| Server not ready | Build takes > 30s | Increase readiness poll timeout |

## Cron Schedule

This scanner is designed to run as a daily cron (e.g. 7 AM local time = `0 11 * * *` UTC for EDT).
See `cron-agent` skill for scheduling instructions and failure-mode handling.
