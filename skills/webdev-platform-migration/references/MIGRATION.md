# Migration Guide — Vite/Express + Supabase App

This guide walks through migrating a Vite + Express + Supabase app from an agent-sandbox deployment to Render.com hosting. It uses a family management app as the reference implementation, but the steps apply to any similar stack.

---

## Current Architecture (Agent Sandbox)

```
[Perplexity Computer Agent]
    → deploys static frontend via deploy_website tool
    → runs Express on localhost:5000 within sandbox
    → cron via schedule_cron → agent calls search_email → bash runner
    → Supabase (unchanged — external service)
```

**Limitations:**
- App URL expires when sandbox is recycled
- Cron depends on agent session being active
- Email scanning requires agent connector token (not portable)

---

## Target Architecture (Render)

```
[GitHub repo: your-org/your-app]
    → Render Web Service (Express + static frontend)
    → Render Cron Job → POST /api/cron/daily-scan
    → Gmail API or inbound email webhook for email intake
    → Supabase (unchanged)
```

**Benefits:**
- Permanent URL (`your-app.onrender.com`)
- Scheduled cron runs reliably without agent
- All infra in code (`render.yaml`)
- ~$0/mo on free tier (with UptimeRobot ping to prevent sleep)

---

## Pre-Migration Checklist

- [ ] `VITE_API_URL` env var in frontend (replaces hardcoded `localhost`)
- [ ] `/api/health` endpoint returns `200`
- [ ] `npm run build` produces `dist/public` + `dist/index.cjs`
- [ ] All secrets in `.env` (not hardcoded)
- [ ] `migration.sql` committed and tested
- [ ] `Dockerfile` committed
- [ ] `render.yaml` committed

---

## Step-by-Step Migration

### 1. Audit for Hardcoded URLs

Search for `localhost` in source:
```bash
grep -r "localhost" src/ --include="*.ts" --include="*.tsx"
```

Replace with env var:
```typescript
// Before
const API = 'http://localhost:5000/api';

// After
const API = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
```

### 2. Add Render Config

Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: family-hub
    runtime: node
    buildCommand: npm ci && npm run build
    startCommand: node dist/index.cjs
    healthCheckPath: /api/health
    envVars:
      - key: NODE_ENV
        value: production
      - key: VITE_SUPABASE_URL
        sync: false
      - key: VITE_SUPABASE_ANON_KEY
        sync: false
      - key: APP_PASSWORD
        sync: false

  - type: cron
    name: daily-scan
    runtime: node
    buildCommand: npm ci
    command: node scripts/cron-trigger.js
    schedule: "0 11 * * *"
    envVars:
      - key: APP_API_URL
        fromService:
          type: web
          name: family-hub
          property: host
```

### 3. Create Cron Trigger Script

```javascript
// scripts/cron-trigger.js
const APP_URL = process.env.APP_API_URL || 'http://localhost:5000';

async function trigger() {
  console.log(`[cron] Triggering daily scan at ${new Date().toISOString()}`);
  const res = await fetch(`${APP_URL}/api/cron/daily-scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  const data = await res.json();
  console.log(`[cron] Result:`, data);
}

trigger().catch(err => {
  console.error('[cron] Error:', err);
  process.exit(1);
});
```

### 4. Add Cron Endpoint to Express

```typescript
// server/routes/cron.ts
import { Router } from 'express';
import { runDailyScan } from '../services/scanner';

const router = Router();

router.post('/daily-scan', async (req, res) => {
  try {
    const result = await runDailyScan();
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

export default router;
```

### 5. Email Intake Options

**Option A — Continue Gmail polling (simplest):**
Replace agent `search_email` with direct Gmail API calls using OAuth2 credentials stored as Render env vars.

Required env vars:
```
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
GMAIL_USER=yourapp@gmail.com
```

**Option B — Twilio SendGrid Inbound Parse (~$1/mo):**
1. Configure SendGrid to parse inbound email at `yourapp@yourdomain.com`
2. SendGrid POSTs parsed email to your `/api/inbox/inbound` endpoint
3. No polling needed — fully event-driven

Inbound endpoint:
```typescript
app.post('/api/inbox/inbound', express.urlencoded({ extended: true }), (req, res) => {
  const { subject, from, text, html } = req.body;
  // process as normal inbox item
  processInboundEmail({ subject, from, body: text || html });
  res.sendStatus(200);
});
```

---

## Post-Migration Verification

```bash
# Health check
curl https://your-app.onrender.com/api/health

# Auth
curl https://your-app.onrender.com/api/auth \
  -X POST -H "Content-Type: application/json" \
  -d '{"password":"your-password"}'

# Manual cron trigger
curl https://your-app.onrender.com/api/cron/daily-scan -X POST
```

---

## Learning Project: OpenClaw / OpenHands

[OpenClaw](https://github.com/All-Hands-AI/OpenHands) (formerly OpenHands) is an open-source AI coding agent you can self-host. It's a great learning project for understanding:

- How agent sandboxes work internally
- Building custom agent tools and connectors
- Self-hosted AI infrastructure patterns

**Note:** OpenClaw is not recommended as the infra layer for a production family hub — complexity vs. benefit is too high. Use it as a local learning environment.

```bash
# Run OpenHands locally (Docker required)
docker run -it --rm \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands-state:/.openhands-state \
  -p 3000:3000 \
  docker.all-hands.dev/all-hands-ai/openhands:0.39
```

---

*Last updated: 2025. Stack: Node 20 + Vite 5 + Supabase + Render.*
