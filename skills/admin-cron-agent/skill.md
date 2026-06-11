# admin:cron-agent

Schedule and run recurring agent tasks as durable cron jobs without sandbox process death, token expiry, or port conflicts.

---

## When to invoke

Trigger on: "set up a daily scan", "schedule this to run every morning", "automate this on a cron", "run this on a schedule", any task that must repeat without user interaction, or any pipeline that has previously failed due to background process death or token isolation errors.

---

## Core Architecture: The Single-Invocation Rule

Agent sandboxes kill all child processes when a bash tool call ends (`& disown` and `nohup` both fail). Every operation — server start, data processing, POST, server kill — must happen inside **one bash call**.

External-tool tokens (e.g. Gmail connector) are only valid when injected directly into a `bash` tool call via `api_credentials`. They cannot pass into Python subprocesses. Therefore the **agent** calls the external tool directly, writes results to a file, then a **single bash call** handles all server-side work.

### Two-Phase Pattern

```
Phase 1 (agent):  Call external tool → write /tmp/data.json
Phase 2 (bash):   Start server → process /tmp/data.json → POST → kill server → write /tmp/results.json
Phase 3 (agent):  Read /tmp/results.json → notify if items found
```

---

## Workflow

### Step 1 — Compute lookback date

```bash
python3 -c "
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y/%m/%d'))
"
```

### Step 2 — Agent calls external tool directly

Call the relevant connector tool (e.g. `search_email`). Write the filtered results to `/tmp/data.json`. Filter criteria example for email:
- Deduplicate by `email_id` (keep first occurrence)
- Remove system/automated senders (noreply@google.com, etc.)

### Step 3 — Single bash invocation

All of the following happen in **one** bash tool call:

```bash
bash scripts/single-invocation-runner.sh /tmp/data.json
```

The runner script (see `scripts/single-invocation-runner.sh`) in one shell:
1. Kills any existing process on the target port
2. Builds the app if `dist/` doesn't exist
3. Starts the server in the background (`&`) within the same shell
4. Polls until the port is ready (max 30s)
5. POSTs each item to the API endpoint
6. Writes results to `/tmp/results.json`
7. Kills the server

### Step 4 — Read results and notify

```bash
cat /tmp/results.json
```

- `total_extracted > 0` → send in-app notification with bullet list of subjects
- `total_extracted == 0` or all skipped → end silently, no notification

---

## Scheduling

Use `pplx-tool schedule_cron` with a standard cron expression in **UTC**. Always confirm with user before creating (each run costs credits).

```bash
pplx-tool schedule_cron <<'JSON'
{
  "cron": "0 11 * * *",
  "name": "Daily Task Name",
  "instructions": "... complete self-contained instructions ..."
}
JSON
```

Cron instructions must be fully self-contained — they receive no conversation history. Include: all step-by-step instructions, file paths, API endpoints, lookback window, and notification logic.

---

## Common failure modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Server killed mid-run | Multiple bash calls | Single-invocation pattern |
| 403 on POST | Proxy URL used | Always use `http://localhost:PORT` |
| External tool 401 | Token passed to subprocess | Agent calls tool directly |
| Port already in use | Previous run leaked | `fuser -k PORT/tcp` before start |

---

## Migration note

On hosted platforms (Render, Railway, Fly.io), cron jobs call the **public API URL** — no local server start needed. The single-invocation pattern is specific to agent sandboxes.

---

## QA checklist

- [ ] Server starts and responds on `/api/health` within 30s
- [ ] Results file written to `/tmp/results.json`
- [ ] Notification sent only when `total_extracted > 0`
- [ ] No notification on empty or all-skipped runs
- [ ] Cron expression is UTC (convert from user's local timezone)
