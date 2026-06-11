# webdev:vite-express

Build and configure full-stack TypeScript apps using Vite (React frontend) and Express (Node.js backend) in a monorepo with shared types, API proxying, Tailwind v3, and a production build pipeline.

---

## When to invoke

Trigger on: "create a new full-stack app", "set up Vite with Express", "configure the API proxy", "Tailwind isn't working", "build is failing", "set up the Dockerfile", "the dev server can't reach the API", or any project scaffolding or build-pipeline work on a Vite + Express stack.

---

## Workflow

### Step 1 — Project structure

```
my-app/
├── client/src/         — React + TypeScript frontend
│   ├── App.tsx
│   ├── main.tsx
│   └── components/
├── client/index.html
├── client/vite.config.ts
├── client/tailwind.config.js
├── server/
│   ├── index.ts        — Express entry point
│   └── routes/
├── shared/types.ts     — shared TypeScript types (optional)
├── package.json        — root scripts
├── tsconfig.json
└── Dockerfile
```

### Step 2 — Root package.json scripts

```json
{
  "scripts": {
    "dev":        "concurrently \"npm run dev:server\" \"npm run dev:client\"",
    "dev:client": "cd client && vite",
    "dev:server": "tsx watch server/index.ts",
    "build":      "vite build --config client/vite.config.ts && tsc -p server/tsconfig.json",
    "start":      "node dist/index.cjs"
  }
}
```

### Step 3 — Vite config with API proxy

```typescript
// client/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: { outDir: '../dist/public', emptyOutDir: true },
  server: {
    proxy: { '/api': { target: 'http://localhost:5000', changeOrigin: true } }
  }
});
```

### Step 4 — Express server

```typescript
// server/index.ts
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(express.json());
app.use('/api', require('./routes'));
app.get('/api/health', (_, res) => res.json({ status: 'ok' }));

if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'public')));
  app.get('*', (_, res) =>
    res.sendFile(path.join(__dirname, 'public', 'index.html'))
  );
}
app.listen(process.env.PORT || 5000);
```

### Step 5 — Tailwind v3

> **Critical:** Use Tailwind **v3** (`^3.4.0`). Tailwind v4 breaks `@tailwind` directives and is not compatible with this setup.

```js
// client/tailwind.config.js
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
};
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 6 — Build and run

```bash
npm run build
# Output: dist/public/ (frontend) + dist/index.cjs (server)

NODE_ENV=production node dist/index.cjs
```

See `references/Dockerfile` for multi-stage Docker packaging.

---

## Environment variables

Use `VITE_` prefix for frontend-accessible vars:

```env
VITE_SUPABASE_URL=...        # accessible in browser
VITE_SUPABASE_ANON_KEY=...   # accessible in browser
VITE_API_URL=...             # set for non-localhost deployments
PORT=5000                    # server only
APP_PASSWORD=...             # server only
```

Always set `VITE_API_URL` when deploying to a non-localhost URL to avoid hardcoded `localhost` references.

---

## Common issues

| Issue | Fix |
|-------|-----|
| `@tailwind` not recognized | Downgrade to `tailwindcss@^3.4.0` |
| nanoid ESM error | Use `nanoid@3` (v4 is ESM-only) |
| API 404 in production | Verify `express.static` path is `dist/public` |
| Frontend can't reach API | Set `VITE_API_URL` env var |
| TypeScript path errors | Check `tsconfig.json` `paths` and `baseUrl` |

---

## QA checklist

- [ ] `npm run build` completes without errors
- [ ] `dist/public/index.html` exists
- [ ] `dist/index.cjs` exists
- [ ] `/api/health` returns `{"status":"ok"}` in production
- [ ] Tailwind classes render in browser
- [ ] No hardcoded `localhost` in frontend source
