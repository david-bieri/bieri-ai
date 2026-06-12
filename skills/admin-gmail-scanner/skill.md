# admin:gmail-scanner

Scan a dedicated Gmail account for structured emails, extract calendar items using subject-line tag fast-path or LLM fallback, deduplicate by gmail_id, and POST results to an app API endpoint.

---

## When to invoke

Trigger on: "scan the family inbox", "process forwarded emails", "run the email scanner", "check for new emails in the hub account", any request to extract structured data from a Gmail intake address, or any request to trigger the daily email pipeline.

Pairs with `admin:cron-agent` for scheduling and `admin:tag-parser` for classification.

---

## Architecture

```
Gmail (dedicated inbox)
    ↓  agent calls search_email directly (token isolation rule)
Filtered email list
    ↓  write to /tmp/emails_to_scan.json
Single bash call (local)  — or —  direct POST (hosted app)
    ↓  POST each email → write results
/tmp/scan_results.json
    ↓  agent reads → notify if new items found
```

**Token isolation rule:** The `gcal` connector's `search_email` must be called by the agent, not from inside bash. Write results to file first; then a single bash call (or a direct POST to the hosted URL) handles all server-side work. See `admin:cron-agent`.

---

## Workflow

### Step 1 — Compute lookback window

```bash
python3 -c "
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y/%m/%d'))
"
```

### Step 2 — Search Gmail (agent call, not bash)

Call `search_email` on the `gcal` connector. Substitute DATE from Step 1:

```json
{
  "queries": [
    "registration deadline", "camp registration", "payment due",
    "school newsletter", "appointment reminder", "practice schedule",
    "sports schedule", "permission slip", "field trip", "vaccine reminder",
    "doctor appointment", "summer program", "enrollment",
    "after:DATE (registration OR deadline OR payment OR appointment OR schedule)"
  ]
}
```

Response shape: `{ email_results: { emails: [...] } }`
Each email has: `email_id`, `subject`, `from_`, `date`, `snippet`, `body`

**Filter before writing:**
- Remove duplicate `email_id` (keep first)
- Remove Google system senders: `noreply@google.com`, `accounts.google.com`, security alerts

### Step 3 — Write to file

Write to `/tmp/emails_to_scan.json` with these exact keys:
```json
[{"gmail_id":"...","subject":"...","from":"...","date":"...","snippet":"...","body":"..."}]
```
Write `[]` if no relevant emails.

### Step 4 — POST the emails

**If the app is hosted (Render, Railway, etc.)** — POST directly to the public URL; no local server start needed:

```python
import json, urllib.request

API = "https://your-app.onrender.com/api/inbox/scan"  # public URL
emails = json.load(open("/tmp/emails_to_scan.json"))
results, total_extracted = [], 0

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
    # ... collect results, write /tmp/scan_results.json
```

**If the app runs locally in the agent sandbox** — use the single-invocation shell script:

```bash
bash scripts/post_emails.sh /tmp/emails_to_scan.json
```

See `scripts/post_emails.sh` for the full local runner (build → start → POST each email → kill → write results).

### Step 5 — Read results and notify

```bash
cat /tmp/scan_results.json
```

Results shape:
```json
{"total_extracted": 2, "results": [
  {"subject": "#CAMP @Clara ...", "status": "extracted", "count": 1},
  {"subject": "Soccer schedule", "status": "skipped", "count": 0}
]}
```

- `total_extracted > 0` → send in-app notification (see Notification Format)
- `total_extracted == 0` → end silently

---

## Notification Format

```
Title: "Family Hub — 3 new inbox items to review"
Body:
• #CAMP @Clara — Registration deadline (1 item)
• #MED @Heidi — Vaccine reminder (1 item)
• #PAY @Cole — Soccer payment due (1 item)
```

---

## Dedicated inbox setup

Use a separate Gmail account (not personal) as the intake address:
1. Create `yourapp@gmail.com`
2. Family members forward relevant emails with `#TAG @Name` in the subject
3. Connect via OAuth as a separate connector (not personal Gmail)
4. Scanner reads only this inbox — no personal email exposure

---

## Scheduling

Designed to run as a daily cron (e.g. 7 AM EDT = `0 11 * * *` UTC). See `admin:cron-agent` for scheduling instructions and failure-mode handling.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 0 emails returned | Wrong account connected | Verify connector points to intake Gmail |
| 403 on POST | Proxy URL used | Use `http://localhost:PORT` |
| Duplicate items | Missing deduplication | Check `gmail_id` filter before writing |
| Token error in bash | `api_credentials` not set | Agent calls `search_email` directly |
| Server not ready | Build takes > 30s | Increase the readiness poll timeout |

---

## QA checklist

- [ ] Connector points to dedicated intake Gmail, not personal account
- [ ] Deduplication runs before writing to file
- [ ] Google system emails filtered out
- [ ] Empty array written if no results (not skipped)
- [ ] Notification sent only when `total_extracted > 0`
