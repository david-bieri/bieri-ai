# webdev:deploy-render

Deploy Node.js web apps and scheduled cron jobs to Render.com with auto-deploy from GitHub, environment variable configuration, health checks, and free-tier optimization.

---

## When to invoke

Trigger on: "deploy this to Render", "set up a Render web service", "move the cron job to Render", "configure auto-deploy from GitHub", "the Render build is failing", "set up environment variables on Render", or any request to host a Node.js app on Render.com.

---

## Render vs. agent-sandbox cron

| Aspect | Agent Sandbox | Render Cron Job |
|--------|--------------|-----------------|
| Server running | Must start it | Always running |
| POST target | `http://localhost:PORT` | `https://your-app.onrender.com` |
| Single-invocation pattern | Required | Not needed |
| Schedule reliability | Agent session must be active | Guaranteed by Render |

On Render, the cron job simply POSTs to the public API — no local server start needed.

---

## Workflow

### Step 1 — Connect GitHub repo

Render Dashboard → New → Web Service → connect GitHub → select repo → set branch to `main`.

### Step 2 — Build and start commands

```
Build Command:  npm ci && npm run build
Start Command:  node dist/index.cjs
```

### Step 3 — Environment variables

Set in Render Dashboard → Environment (not in `.env` — that's for local only):

```
NODE_ENV=production
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
APP_PASSWORD=your-password
```

Render sets `PORT` automatically — your server must use `process.env.PORT`.

### Step 4 — Health check

Set health check path to `/api/health` in Render settings. Express must respond `200`:

```typescript
app.get('/api/health', (_, res) => res.json({ status: 'ok' }));
```

### Step 5 — Cron job (replacing agent-sandbox cron)

New → Cron Job → Command: `node scripts/cron-trigger.js` → Schedule: `0 11 * * *` (UTC)

```javascript
// scripts/cron-trigger.js
const APP_URL = process.env.APP_API_URL || 'https://your-app.onrender.com';
const res = await fetch(`${APP_URL}/api/cron/daily-scan`, { method: 'POST' });
console.log('Result:', await res.json());
```

Add the cron endpoint in Express:
```typescript
app.post('/api/cron/daily-scan', async (req, res) => {
  const result = await runDailyScan();
  res.json(result);
});
```

---

## render.yaml (infrastructure as code)

```yaml
services:
  - type: web
    name: my-app
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
          name: my-app
          property: host
```

---

## Free tier limits

| Limit | Free Tier |
|-------|-----------|
| Web service | 1 instance, sleeps after 15 min inactivity |
| Cron jobs | 1 free |
| Build minutes | 400/mo |

**Tip:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping `/api/health` every 5 min to prevent sleep.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Verify `npm run build` works locally |
| 503 on cold start | Free tier sleeps — use UptimeRobot |
| Env vars missing | Set in Render Dashboard, not `.env` |
| Cron not firing | Verify schedule is UTC; check command exits 0 |
| 404 on all routes | Check `express.static` points to `dist/public` |

---

## QA checklist

- [ ] `npm run build` passes locally before pushing
- [ ] `render.yaml` committed to repo root
- [ ] All env vars set in Render Dashboard
- [ ] `/api/health` returns 200 after deploy
- [ ] Auto-deploy fires on `git push origin main`
- [ ] Cron trigger script exits 0 on success
