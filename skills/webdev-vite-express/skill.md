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

### Step 2 — Root package.json

```json
{
  "scripts": {
    "dev":        "concurrently \"npm run dev:server\" \"npm run dev:client\"",
    "dev:client": "cd client && vite",
    "dev:server": "tsx watch server/index.ts",
    "build":      "vite build --config client/vite.config.ts && tsc -p server/tsconfig.json",
    "start":      "node dist/index.cjs"
  },
  "dependencies": {
    "express": "^4.18.2",
    "@supabase/supabase-js": "^2.39.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "concurrently": "^8.2.0",
    "tsx": "^4.7.0"
  }
}
```

> Build-time Tailwind plugins are the exception to "dev deps" — see the Tailwind section.

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
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api', require('./routes'));
app.get('/api/health', (_, res) => res.json({ status: 'ok' }));

if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'public')));
  app.get('*', (_, res) =>
    res.sendFile(path.join(__dirname, 'public', 'index.html'))
  );
}
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

### Step 5 — Tailwind v3

> **Critical — both rules must be followed:**
> 1. Use Tailwind **v3** (`^3.4.0`). v4 breaks `@tailwind` directives and is not compatible with this setup.
> 2. The config must be **`tailwind.config.js`** (plain CJS `module.exports`). Do **not** use `tailwind.config.ts`.

**Why no `.ts` config?** tailwindcss v3 loads a `.ts` config via jiti. As of jiti v2 the default export changed from a callable function to an object (`createJiti()`), but tailwindcss v3's `load-config.js` still calls the old `jiti(filename, opts)` pattern. It fails **silently** on clean installs, crashing the `vite:css` transform with a CSS content dump and `Build failed`.

```js
// client/tailwind.config.js  ← must be .js, not .ts
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [require('tailwindcss-animate')],  // plugins via require(), not import
};
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Tailwind plugins must be in `dependencies`.** Any plugin used at build time (`tailwindcss-animate`, `@tailwindcss/typography`, etc.) must be in `dependencies`, not `devDependencies` — hosts like Render run `npm ci` without dev deps, so the plugin goes missing and the build fails.

**Never install `@tailwindcss/vite`.** That's the v4 Vite plugin; installed alongside Tailwind v3 (even unused) it pulls in a v4 engine that conflicts with the v3 PostCSS pipeline. Remove it if present.

### Step 6 — Build and run

```bash
npm run build
# Output: dist/public/ (frontend) + dist/index.cjs (server)

NODE_ENV=production node dist/index.cjs
```

See `references/Dockerfile` for a multi-stage Docker build (node:20-alpine build stage → minimal runtime, exposes 5000, `NODE_ENV=production`).

---

## Node version

Vite 7 requires **Node `^20.19.0 || >=22.12.0`**. Older 20.x releases (20.11.x, 20.18.x) fail the build with a silent `Exited with status 1`. Pin explicitly:

```
# .node-version
20.19.0
```
```json
// package.json
{ "engines": { "node": "^20.19.0 || >=22.12.0" } }
```

---

## Build script and tsx

If the project uses npm `overrides` (e.g. aliasing `@esbuild-kit/esm-loader → tsx` for drizzle-kit), the `.bin/tsx` symlink may point to the wrong place. Call tsx's CJS entry directly:

```json
{ "scripts": { "build": "node node_modules/tsx/dist/cli.cjs script/build.ts" } }
```

After any `package.json` change, regenerate the lock file before committing:
```bash
npm install --package-lock-only
npm ci --dry-run   # verify before pushing
```

---

## Environment variables

Use the `VITE_` prefix for frontend-accessible vars:

```env
VITE_SUPABASE_URL=...        # accessible in browser
VITE_SUPABASE_ANON_KEY=...   # accessible in browser
VITE_API_URL=...             # set for non-localhost deployments
PORT=5000                    # server only
APP_PASSWORD=...             # server only
```

Access: frontend via `import.meta.env.VITE_*`; backend via `process.env.*`. Always set `VITE_API_URL` when deploying to a non-localhost URL to avoid hardcoded `localhost` references.

---

## Common issues

| Issue | Fix |
|-------|-----|
| `@tailwind` not recognized | Downgrade to Tailwind v3: `npm install tailwindcss@^3.4.0` |
| `tailwind.config.ts` crashes on CI | Convert to `tailwind.config.js` with `module.exports` |
| Tailwind plugin missing on CI | Move plugin to `dependencies` (not devDeps) |
| `@tailwindcss/vite` conflicts | Remove it — incompatible with Tailwind v3 PostCSS setup |
| nanoid ESM error | Use `nanoid@3` (v4 is ESM-only) |
| API 404 in production | Verify `express.static` serves from `dist/public` |
| Frontend can't reach API | Set `VITE_API_URL` env var |
| Vite EADDRINUSE | Change `server.port` in vite.config.ts |
| `tsx: not found` on CI | Use `node node_modules/tsx/dist/cli.cjs` — see Build script section |
| TypeScript path errors | Check `tsconfig.json` `paths` and `baseUrl` |

---

## QA checklist

- [ ] `npm run build` completes without errors
- [ ] Node version pinned (`.node-version` / `engines`)
- [ ] `dist/public/index.html` exists
- [ ] `dist/index.cjs` exists
- [ ] `/api/health` returns `{"status":"ok"}` in production
- [ ] Tailwind config is `.js`; plugins in `dependencies`; no `@tailwindcss/vite`
- [ ] Tailwind classes render in browser
- [ ] No hardcoded `localhost` in frontend source
