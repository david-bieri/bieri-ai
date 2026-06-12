# webdev:deploy-render

Deploy Node.js web apps and scheduled cron jobs to Render.com with auto-deploy from GitHub, environment variable configuration, health checks, and free-tier optimization.

---

## When to invoke

Trigger on: "deploy this to Render", "set up a Render web service", "move the cron job to Render", "configure auto-deploy from GitHub", "the Render build is failing", "Exited with status 1", "set up environment variables on Render", or any request to host a Node.js app on Render.com.

---

## Render vs. agent-sandbox cron

| Aspect | Agent Sandbox | Render Cron Job |
|--------|--------------|-----------------|
| Server already running | No — must start it | Yes — app is always up |
| POST target | `http://localhost:PORT` | `https://your-app.onrender.com` |
| Single-invocation pattern | Required | Not needed |
| Token isolation | Yes — agent writes file | Not applicable |
| Schedule reliability | Depends on agent session | Guaranteed by Render |

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

> **Dashboard vs. render.yaml:** a Build Command set manually in the dashboard overrides `render.yaml`. If you use `render.yaml`, verify the dashboard field matches (or is blank).

### Step 3 — Pin the Node version

Always pin an explicit Node version. Vite 7 requires `^20.19.0 || >=22.12.0`; Render's default `20` may resolve to an older 20.x and fail **silently** (`Exited with status 1`, no useful output). Set it in both places:

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

The `.node-version` file takes precedence if present.

### Step 4 — Environment variables

Set in Render Dashboard → Environment (not in `.env` — that's local only):

```
NODE_ENV=production
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
APP_PASSWORD=your-password
```

Render sets `PORT` automatically — the server must use `process.env.PORT`.

> **VITE_ prefix at runtime:** env vars set in Render reach the server process with their exact names. If you set `VITE_SUPABASE_URL`, the server must read `process.env.VITE_SUPABASE_URL` — not `process.env.SUPABASE_URL`. Read both to be safe:
> ```typescript
> const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || '';
> ```

### Step 5 — Health check

Set the health check path to `/api/health` in Render settings. Express must respond `200`:

```typescript
app.get('/api/health', (_, res) => res.json({ status: 'ok' }));
```

### Step 6 — Cron job (replacing agent-sandbox cron)

New → Cron Job → Build Command `npm ci` → Command `node scripts/cron-trigger.js` → Schedule `0 11 * * *` (UTC).

```javascript
// scripts/cron-trigger.js
const APP_URL = process.env.APP_API_URL || 'https://your-app.onrender.com';
const res = await fetch(`${APP_URL}/api/cron/daily-scan`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
});
console.log('Cron result:', await res.json());
```

Add the cron endpoint in Express:
```typescript
app.post('/api/cron/daily-scan', async (req, res) => {
  const result = await runDailyScan();
  res.json(result);
});
```

---

## Auto-deploy from GitHub

Render redeploys automatically on push to `main`:
```bash
git add .
git commit -m "feat: update"
git push origin main   # Render picks up the push and redeploys
```
To disable: Render Dashboard → Settings → Auto-Deploy → Off.

---

## render.yaml (infrastructure as code)

```yaml
# render.yaml
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

## Diagnosing "Exited with status 1"

Render's `Exited with status 1` is not one error — read the full log to find the actual failing line:

| Log pattern | Root cause | Fix |
|-------------|-----------|-----|
| `tsx: not found` | `.bin/tsx` symlink broken by npm overrides | Use `node node_modules/tsx/dist/cli.cjs` |
| `npm ERR! Missing: @esbuild-kit/...` | Lock file out of sync with package.json | `npm install --package-lock-only` and commit |
| `[vite:css] Cannot find module '@tailwindcss/typography'` | Plugin in devDeps; host skips devDeps | Move it to `dependencies` |
| CSS content dumped then Build failed | `tailwind.config.ts` + jiti v1/v2 incompatibility | Rename to `tailwind.config.js` with `module.exports` |
| `supabaseUrl is required` | Server reads bare name; Render has VITE_ prefix | Read both: `process.env.X \|\| process.env.VITE_X` |
| Silent exit, no useful output | Node below Vite 7 minimum (< 20.19.0) | Pin `nodeVersion: 20.19.0` |

---

## Free tier limits

| Limit | Free Tier |
|-------|-----------|
| Web service | 1 instance, sleeps after 15 min inactivity |
| Cron jobs | 1 free |
| Build minutes | 400/mo |
| Bandwidth | 100 GB/mo |

**Tip:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping `/api/health` every 5 min and prevent the service from sleeping.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails silently | Pin Node version — `nodeVersion: 20.19.0` |
| Builds locally but fails on Render | `rm -rf node_modules && npm ci && npm run build` locally to simulate a clean install |
| 503 on cold start / wake | Free tier sleeps — ping with UptimeRobot |
| Env vars missing at runtime | Set in Render Dashboard with the exact key names the server reads |
| Cron not firing | Verify schedule is UTC; confirm command exits 0 |
| 404 on all routes | Check `express.static` points to `dist/public` |

---

## QA checklist

- [ ] `npm run build` passes locally before pushing
- [ ] Node version pinned (`.node-version` and/or `render.yaml nodeVersion`)
- [ ] `render.yaml` committed to repo root
- [ ] All env vars set in Render Dashboard with the names the server reads
- [ ] `/api/health` returns 200 after deploy
- [ ] Auto-deploy fires on `git push origin main`
- [ ] Cron trigger script exits 0 on success
