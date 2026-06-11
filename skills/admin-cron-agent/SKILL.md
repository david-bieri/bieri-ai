---
name: admin-cron-agent
description: "Schedule and run recurring agent tasks as durable cron jobs. Use when setting up any periodic automation: email scanning, data sync, daily digests, health checks, or any task that must run on a fixed schedule. Covers single-invocation pattern to avoid background-process sandbox death, external-tool token isolation, and result-file handoff between agent and bash."
metadata:
  version: '1.0'
  domain: universal
  author: bieri-ai
---

# Cron Agent

## When to Use This Skill

Load this skill when:
- The user asks to schedule a recurring task (daily, weekly, hourly)
- You need to set up an automated pipeline that runs without user interaction
- A task requires reading from an external service (email, API) on a schedule
- You need to avoid common sandbox pitfalls: process death, token expiry, port conflicts

## Core Architecture Principles

### The Single-Invocation Rule
**Problem:** In agent sandboxes, background processes (`& disown`, `nohup`) are killed when the bash tool call ends.
**Solution:** Every cron-triggered operation — server start, data processing, POST, server kill — must happen inside a **single bash tool call**.

### Token Isolation Rule
**Problem:** External-tool tokens (e.g. `api_credentials=["external-tools"]`) are only valid when injected directly into a `bash` tool call. They cannot be passed into Python scripts called from bash.
**Solution:** The **agent** calls external tools directly (e.g. `search_email`), writes results to a file, then a single bash call handles all server-side work using those files.

### Two-Phase Pattern
```
Phase 1 (agent): Call external tool → write /tmp/data.json
Phase 2 (bash):  Start server → process /tmp/data.json → POST → kill server → write /tmp/results.json
Phase 3 (agent): Read /tmp/results.json → notify if needed
```

## Instructions

### Step 1 — Compute Lookback Date
```bash
python3 -c "
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y/%m/%d'))
"
```

### Step 2 — Agent Calls External Tool
Call the relevant external tool directly (e.g. `search_email`, `list_events`).
Write filtered results to `/tmp/data.json` using the bash tool.

Filter criteria (example for email):
- Deduplicate by `email_id` (keep first occurrence)
- Remove system/automated senders (e.g. noreply@google.com)

### Step 3 — Single Bash Invocation
Reference the bundled runner script: `scripts/single-invocation-runner.sh`

This script in one shell:
1. Builds/starts the app server
2. Waits for readiness (poll on port)
3. POSTs each item to the API endpoint
4. Writes results to `/tmp/results.json`
5. Kills the server

```bash
bash /path/to/scripts/single-invocation-runner.sh /tmp/data.json
```

### Step 4 — Read Results and Notify
```bash
cat /tmp/results.json
```

- If `total_extracted > 0`: send in-app notification with summary
- If `total_extracted == 0` or all skipped: end silently

## Scheduling

### Creating a Cron Job
Use `pplx-tool schedule_cron` with:
- `cron`: standard cron expression in **UTC** (convert user's local time)
- `run_at`: ISO timestamp for one-time scheduled runs
- Always confirm with user before creating (costs credits per run)

```bash
pplx-tool schedule_cron <<'JSON'
{
  "cron": "0 11 * * *",
  "name": "Daily Task Name",
  "instructions": "... full agent instructions ..."
}
JSON
```

### Cron Instructions Must Be Self-Contained
The cron body receives no conversation history. Include:
- All step-by-step instructions
- File paths for scripts
- API endpoint URLs
- Lookback window
- Notification logic

## Common Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Server killed mid-run | Multiple bash calls | Single-invocation pattern |
| 403 on POST | Proxy URL expired | Use `localhost:PORT` |
| External tool 401 | Token in subprocess | Agent calls tool directly |
| Port already in use | Previous run leaked | Kill port before start |

## Hosted App Pattern (Render / Railway / Fly.io)

When the app is deployed to a public host, the cron **does not start a server** — it POSTs directly to the public URL. This is simpler and more reliable.

```
Phase 1 (agent): Call external tool → write /tmp/data.json
Phase 2 (bash):  POST each item to https://your-app.onrender.com/api/... → write /tmp/results.json
Phase 3 (agent): Read /tmp/results.json → notify if needed
```

Example Phase 2 for a hosted app:
```python
import json, urllib.request

API = "https://your-app.onrender.com/api/inbox/scan"  # public URL
emails = json.load(open("/tmp/emails_to_scan.json"))

for email in emails:
    payload = json.dumps({...}).encode()
    req = urllib.request.Request(API, data=payload,
                                 headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    # handle resp...
```

> **Free tier cold start:** Render free tier sleeps after 15 min. The first POST of the day may take 30–60s to wake the instance. Use a 60s timeout on the first request, or set up UptimeRobot to keep the instance warm.

The single-invocation build+start+kill pattern is only needed in the agent sandbox where the app runs locally.
