# webdev:platform-migration

Plan and execute migration of a web app from an agent-hosted sandbox to a self-hosted production platform: portability audit, environment variable cleanup, Render + Supabase target stack, cost estimate, and documentation requirements.

---

## When to invoke

Trigger on: "migrate off Perplexity", "make this app platform-independent", "what if I want to move this later", "how do I host this myself", "audit the app for portability", "set up Render instead of the sandbox", any request to reduce platform lock-in or move to a self-hosted deployment.

---

## Portability audit

Run through this checklist before migrating:

### Environment variables
- [ ] All secrets in `.env` (none hardcoded in source)
- [ ] `VITE_API_URL` is configurable (no hardcoded `localhost`)
- [ ] `.env.example` documents every required variable

### Database
- [ ] Database URL in environment variable
- [ ] Migration SQL committed and runnable standalone
- [ ] No platform-specific DB services

### File storage
- [ ] No local filesystem writes that must persist
- [ ] `/tmp` usage is acceptable (ephemeral)

### Cron jobs
- [ ] Schedule documented (not only in agent conversation)
- [ ] POST endpoint exists for external cron trigger
- [ ] No hard dependency on agent-sandbox single-invocation pattern

### Build
- [ ] `npm run build` works standalone
- [ ] `Dockerfile` committed
- [ ] `package.json` scripts are self-documenting

---

## Workflow

### Step 1 — Run portability audit

Check for hardcoded `localhost` in source:
```bash
grep -r "localhost" src/ --include="*.ts" --include="*.tsx"
```
Replace with: `import.meta.env.VITE_API_URL || 'http://localhost:5000'`

### Step 2 — Add missing files

Files every portable app must have:

| File | Purpose |
|------|---------|
| `README.md` | Setup, build, and run instructions |
| `DEPLOYMENT.md` | Platform-specific deploy steps |
| `MIGRATION.md` | How to move between platforms |
| `CHANGELOG.md` | Version history |
| `.env.example` | All environment variables documented |
| `Dockerfile` | Container build for any platform |
| `render.yaml` | Render infrastructure-as-code |

### Step 3 — Set up Render

See `webdev:deploy-render` for full setup. Core steps:
1. Create Render Web Service from GitHub repo
2. Set all environment variables in Render Dashboard
3. Deploy and verify `/api/health` responds 200

### Step 4 — Migrate cron jobs

Replace agent `schedule_cron` with Render Cron Job:
1. Write `scripts/cron-trigger.js` to POST to `APP_API_URL`
2. Add cron job in `render.yaml`
3. Cancel the agent-scheduled cron (if any)

### Step 5 — Migrate email intake

**Option A — Keep Gmail polling:** Set up Gmail API credentials as Render env vars; replace agent connector with direct API call.

**Option B — Inbound email webhook (recommended for reliability):**
- Twilio SendGrid inbound parse (~$1/mo)
- Receives forwarded emails as HTTP POST to `/api/inbox/inbound`
- Eliminates polling entirely; fully event-driven

```typescript
app.post('/api/inbox/inbound', express.urlencoded({ extended: true }), (req, res) => {
  const { subject, from, text } = req.body;
  processInboundEmail({ subject, from, body: text });
  res.sendStatus(200);
});
```

---

## Migration target stack

| Component | Agent Sandbox | Self-Hosted |
|-----------|--------------|-------------|
| Frontend | Agent deploy tool | Render static / CDN |
| Backend | `localhost:5000` | Render Web Service |
| Database | Supabase | Supabase (unchanged) |
| Cron | `schedule_cron` | Render Cron Job |
| Email | Agent connector | Gmail API or SendGrid |
| Cost | ~$0 (included) | ~$0–8/mo (free tiers) |

---

## Learning project: OpenHands (OpenClaw)

[OpenHands](https://github.com/All-Hands-AI/OpenHands) is an open-source AI coding agent for self-hosting. Useful for understanding how agent sandboxes work and building custom agent tooling. Not recommended as production infra for a family hub (complexity–benefit ratio too high), but excellent as a local learning environment.

```bash
docker run -it --rm \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  docker.all-hands.dev/all-hands-ai/openhands:0.39
```

---

## QA checklist

- [ ] No hardcoded `localhost` in frontend source
- [ ] `VITE_API_URL` env var wired up
- [ ] All required docs committed (`README`, `DEPLOYMENT`, `MIGRATION`, `CHANGELOG`, `.env.example`, `Dockerfile`)
- [ ] `render.yaml` committed
- [ ] App builds and `/api/health` responds on Render URL
- [ ] Cron fires on schedule (check Render cron logs)
- [ ] Old agent cron cancelled after Render cron confirmed working
