---
name: webdev-deploy-render
description: "Deploy Node.js web apps and scheduled jobs to Render.com. Use when moving a Vite/Express app from an agent sandbox to a hosted platform, configuring web services and cron jobs on Render, setting environment variables, connecting a GitHub repo for auto-deploy, or migrating from a local cron pattern to a hosted one. Covers free tier, build commands, health checks, and Render vs. agent-sandbox cron differences."
metadata:
  version: '1.0'
  domain: webdev
  author: bieri-ai
---

# Deploy to Render

## When to Use This Skill

Load this skill when:
- Deploying a Node.js/Express app to a permanent hosted URL
- Setting up a Render Web Service from a GitHub repo
- Configuring cron jobs on Render (vs. agent-sandbox cron)
- Moving from Perplexity-hosted to self-hosted deployment

## Render vs. Agent Sandbox Cron

| Aspect | Agent Sandbox | Render Cron Job |
|--------|--------------|-----------------|
| Server already running | No — must start it | Yes — app is always up |
| POST target | `http://localhost:PORT` | `https://your-app.onrender.com` |
| Single-invocation pattern | Required | Not needed |
| Token isolation | Yes — agent writes file | Not applicable |
| Schedule reliability | Depends on agent session | Guaranteed by Render |

**On Render:** cron job simply makes a POST to the public API — no local server start needed.

## Render Setup — Web Service

### Step 1 — Connect GitHub Repo
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub account and select your repo
3. Set **branch** to `main`

### Step 2 — Configure Build & Start
```
Build Command:  npm ci && npm run build
Start Command:  node dist/index.cjs
```

> **Dashboard vs. render.yaml:** If a Build Command was previously set manually in the Render dashboard, it overrides `render.yaml`. Verify the dashboard field matches.

### Step 3 — Pin Node Version

Always pin an explicit Node version. Vite 7 requires `^20.19.0 || >=22.12.0` — Render's default `20` resolves to whatever 20.x is available, which may be older than 20.19.0 and will fail silently.

Set in **both** places:
```
# .node-version (committed to repo)
20.19.0
```
```yaml
# render.yaml
services:
  - type: web
    runtime: node
    nodeVersion: 20.19.0
```

Or set it in the Render Dashboard → Settings → Node Version. The `.node-version` file takes precedence if present.

### Step 4 — Environment Variables
Add in Render Dashboard → Environment:
```
NODE_ENV=production
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
APP_PASSWORD=your-password
PORT=10000  # Render sets this automatically via $PORT
```

> **Critical — VITE_ prefix at runtime:** Environment variables set in Render are available to the server process at runtime with their exact names. If you set `VITE_SUPABASE_URL` in the dashboard, the server must read `process.env.VITE_SUPABASE_URL` — not `process.env.SUPABASE_URL`. These are different keys.
>
> Pattern to handle both names safely:
> ```typescript
> const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || '';
> ```

### Step 5 — Health Check
Set health check path to `/api/health` in Render settings.
Your Express server must respond with `200` on this route.

```typescript
app.get('/api/health', (_, res) => res.json({ status: 'ok' }));
```

## Render Cron Job

### Setup
1. New → Cron Job
2. Build Command: `npm ci`
3. Command: `node scripts/cron-trigger.js`
4. Schedule: `0 11 * * *` (UTC)

### Cron Script (Render)
```javascript
// scripts/cron-trigger.js
const APP_URL = process.env.APP_API_URL || 'https://your-app.onrender.com';

async function run() {
  // No server start needed — app is already running
  const response = await fetch(`${APP_URL}/api/cron/daily-scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  const result = await response.json();
  console.log('Cron result:', result);
}

run().catch(console.error);
```

### Cron Endpoint (Express)
```typescript
app.post('/api/cron/daily-scan', async (req, res) => {
  // Trigger your scan logic here
  const results = await runDailyScan();
  res.json(results);
});
```

## Free Tier Constraints

| Limit | Free Tier |
|-------|-----------|
| Web service | 1 instance, sleeps after 15min inactivity |
| Cron jobs | 1 free cron |
| Build minutes | 400/mo |
| Bandwidth | 100 GB/mo |

**Tip:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping `/api/health` every 5 min and prevent the service from sleeping.

## Auto-Deploy from GitHub

Render automatically redeploys when you push to `main`:
```bash
git add .
git commit -m "feat: update"
git push origin main
# Render picks up the push and redeploys automatically
```

To disable auto-deploy: Render Dashboard → Settings → Auto-Deploy → Off

## render.yaml (Infrastructure as Code)

```yaml
# render.yaml
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
        sync: false  # set manually in dashboard
      - key: VITE_SUPABASE_ANON_KEY
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

## render.yaml with nodeVersion

```yaml
services:
  - type: web
    name: my-app
    runtime: node
    nodeVersion: 20.19.0          # explicit — never omit
    buildCommand: npm ci && npm run build
    startCommand: node dist/index.cjs
    healthCheckPath: /api/health
    envVars:
      - key: NODE_ENV
        value: production
      - key: VITE_SUPABASE_URL
        sync: false               # set manually in dashboard
      - key: VITE_SUPABASE_ANON_KEY
        sync: false
      - key: APP_PASSWORD
        sync: false
```

## Diagnosing "Exited with status 1"

Render's `Exited with status 1` is not one error — it can mean several different things. Read the full log to find the actual error line:

| Log pattern | Root cause | Fix |
|-------------|-----------|-----|
| `tsx: not found` | `.bin/tsx` symlink broken by npm overrides | Use `node node_modules/tsx/dist/cli.cjs` |
| `npm ERR! Missing: @esbuild-kit/...` | Lock file out of sync with package.json | Run `npm install --package-lock-only` and commit |
| `[vite:css] Cannot find module '@tailwindcss/typography'` | Plugin in devDeps, host skips devDeps | Move to `dependencies` |
| CSS content dumped then Build failed | `tailwind.config.ts` + jiti v1/v2 incompatibility | Rename to `tailwind.config.js` with `module.exports` |
| `supabaseUrl is required` | Server reads bare env var name, Render has VITE_ prefix | Read both: `process.env.X \|\| process.env.VITE_X` |
| Silent exit, no useful output | Node version below Vite 7 minimum (< 20.19.0) | Pin `nodeVersion: 20.19.0` in render.yaml |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails silently | Check Node version — pin `nodeVersion: 20.19.0` |
| `npm run build` works locally but fails on Render | Run `rm -rf node_modules && npm ci && npm run build` locally to simulate clean install |
| 503 on wake | Free tier sleeps; ping with UptimeRobot |
| Env vars missing at runtime | Must be set in Render Dashboard with exact key names the server reads |
| Cron not firing | Check schedule is UTC; verify command exits 0 |
| 404 on all routes | Verify `express.static` points to `dist/public` |
