---
name: webdev-vite-express
description: "Build and configure full-stack web apps using Vite (React/TypeScript frontend) + Express (Node.js backend) in a monorepo structure. Use when creating a new full-stack app, setting up the build pipeline, configuring API proxying, writing shared types, or preparing for containerized deployment. Covers npm workspaces, Tailwind v3, production build, and Docker packaging."
metadata:
  version: '1.0'
  domain: webdev
  author: bieri-ai
---

# Vite + Express

## When to Use This Skill

Load this skill when:
- Creating a new full-stack TypeScript app from scratch
- Setting up API proxying between Vite dev server and Express
- Building and bundling for production deployment
- Adding Tailwind CSS v3 to a Vite project
- Containerizing a Vite/Express app with Docker

## Project Structure

```
my-app/
├── client/               # Vite + React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── components/
│   ├── index.html
│   ├── vite.config.ts
│   └── tailwind.config.js
├── server/               # Express backend
│   ├── index.ts
│   └── routes/
├── shared/               # Shared types (optional)
│   └── types.ts
├── package.json          # Root — build scripts
├── tsconfig.json
├── Dockerfile
└── .env
```

## Key Configuration Files

### package.json (root)
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:server\" \"npm run dev:client\"",
    "dev:client": "cd client && vite",
    "dev:server": "tsx watch server/index.ts",
    "build": "vite build --config client/vite.config.ts && tsc -p server/tsconfig.json",
    "start": "node dist/index.cjs"
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

### vite.config.ts
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../dist/public',  // serve static from Express
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
```

### server/index.ts
```typescript
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());

// API routes
app.use('/api', require('./routes'));

// Health check
app.get('/api/health', (_, res) => res.json({ status: 'ok' }));

// Serve frontend in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'public')));
  app.get('*', (_, res) =>
    res.sendFile(path.join(__dirname, 'public', 'index.html'))
  );
}

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

## Tailwind v3 Setup

> **Critical rules — both must be followed:**
> 1. Use Tailwind **v3** (`^3.4.0`). v4 breaks `@tailwind` directives.
> 2. Config file must be **`tailwind.config.js`** (plain CJS `module.exports`). Do NOT use `tailwind.config.ts`.

### Why no .ts config?
tailwindcss v3 loads `.ts` config via jiti. As of jiti v2, the default export changed from a callable function to an object (`createJiti()` is the new API). tailwindcss v3's `load-config.js` still calls the old `jiti(filename, opts)` pattern — it fails silently on clean installs, causing the `vite:css` transform to crash with a CSS content dump and `Build failed`.

```js
// tailwind.config.js  ← must be .js, not .ts
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [require('tailwindcss-animate')],  // plugins via require(), not import
};
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Tailwind plugins must be in `dependencies`
Any Tailwind plugin used at build time (`tailwindcss-animate`, `@tailwindcss/typography`, etc.) must be in **`dependencies`**, not `devDependencies`. Hosts like Render run `npm ci` without `--include=dev` by default — plugins in devDeps will be missing and the build fails.

```json
{
  "dependencies": {
    "tailwindcss": "^3.4.0",
    "tailwindcss-animate": "^1.0.7",
    "@tailwindcss/typography": "^0.5.15"
  }
}
```

### Never install `@tailwindcss/vite`
`@tailwindcss/vite` is the v4 Vite plugin. Installing it alongside Tailwind v3 (even unused) pulls in a v4 engine that conflicts with the v3 PostCSS pipeline. Remove it entirely if present.

## Environment Variables

Use `VITE_` prefix for frontend-accessible vars:
```env
VITE_SUPABASE_URL=...      # accessible in frontend
VITE_SUPABASE_ANON_KEY=... # accessible in frontend
PORT=5000                   # server-only
APP_PASSWORD=...            # server-only
```

Access in code:
```typescript
// Frontend
const url = import.meta.env.VITE_SUPABASE_URL;

// Backend
const port = process.env.PORT;
```

## Production Build

```bash
# Build frontend + server
npm run build

# Output:
# dist/public/     — static frontend assets
# dist/index.cjs   — compiled server

# Start production server
NODE_ENV=production node dist/index.cjs
```

## Docker

See `references/Dockerfile` for a multi-stage Docker build:
- Stage 1: `node:20-alpine` build
- Stage 2: minimal runtime image
- Exposes port 5000
- Sets `NODE_ENV=production`

## Node Version

Vite 7 requires **Node `^20.19.0 || >=22.12.0`**. Older Node 20.x releases (e.g. 20.11.x, 20.18.x) will fail the build with a silent `Exited with status 1`. Pin explicitly:

```
# .node-version
20.19.0
```

```json
// package.json
{ "engines": { "node": "^20.19.0 || >=22.12.0" } }
```

## Build Script and tsx

If your project uses npm `overrides` (e.g. to alias `@esbuild-kit/esm-loader → tsx` for drizzle-kit), the `.bin/tsx` symlink may point to the wrong location. Call tsx's CJS entry directly instead:

```json
{ "scripts": { "build": "node node_modules/tsx/dist/cli.cjs script/build.ts" } }
```

After any `package.json` change, regenerate the lock file before committing:
```bash
npm install --package-lock-only
npm ci --dry-run  # verify before pushing
```

## Common Issues

| Issue | Fix |
|-------|-----|
| `@tailwind` not recognized | Downgrade to Tailwind v3: `npm install tailwindcss@^3.4.0` |
| `tailwind.config.ts` crashes on CI | Convert to `tailwind.config.js` with `module.exports` — see Tailwind section above |
| Tailwind plugin missing on CI | Move plugin to `dependencies` (not devDeps) |
| `@tailwindcss/vite` conflicts | Remove it — incompatible with Tailwind v3 PostCSS setup |
| nanoid ESM error | Use nanoid v3: `npm install nanoid@3` |
| API 404 in production | Check `express.static` serves from correct `dist/public` path |
| Vite EADDRINUSE | Change `server.port` in vite.config.ts |
| TypeScript path errors | Verify `tsconfig.json` `paths` and `baseUrl` |
| `tsx: not found` on CI | Use `node node_modules/tsx/dist/cli.cjs` — see Build Script section above |
