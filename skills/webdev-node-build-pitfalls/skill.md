# webdev:node-build-pitfalls

A diagnostic reference for Node.js builds that pass locally but fail on a clean CI/CD host — seven known failure modes, each with symptom, root cause, and fix.

---

## When to invoke

Trigger on: "the build passes locally but fails on Render", "Exited with status 1", "tsx: not found", "Cannot find module @tailwindcss/...", "lock file out of sync", "vite:css transform crashed", "supabaseUrl is required at startup", or any CI/CD build failure on Render, Railway, Fly.io, or GitHub Actions.

---

## The Golden Rule

> **Always simulate a clean install before pushing.** The only reliable way to catch CI failures locally is:
> ```bash
> rm -rf node_modules && npm ci && npm run build
> ```
> If this passes locally, it will pass on Render. If it fails locally, fix it before pushing.

---

## Pitfall 1 — tailwind.config.ts crashes the vite:css transform

### Symptom
Build log shows the full CSS file contents dumped as a string, followed by:
```
plugin: 'vite:css'
hook: 'transform'
==> Build failed
```
No explicit error message — just CSS content then failure.

### Root Cause
tailwindcss v3 loads `.ts` configs via jiti. In jiti v2, the default export changed from a callable function to an object (`createJiti()` is the new API). tailwindcss v3's `load-config.js` still calls the old v1 pattern:
```js
jiti(filename, { interopDefault: true, transform: ... })
```
This fails on a clean install with jiti v2, crashing the PostCSS transform mid-execution. The crash manifests as the CSS content being logged (Vite's error serialization), not a clean error message.

### Fix
Convert `tailwind.config.ts` → `tailwind.config.js` using CJS `module.exports`. No jiti involved — loaded directly by `require()`.

```js
// tailwind.config.js  ← must be .js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./client/src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [require('tailwindcss-animate')],
};
```

**Never use `.ts` for Tailwind config with tailwindcss v3.**

---

## Pitfall 2 — Tailwind plugins missing on CI

### Symptom
```
[vite:css] [postcss] Cannot find module '@tailwindcss/typography'
Require stack:
- /opt/render/project/src/tailwind.config.ts
```

### Root Cause
Tailwind plugins (`tailwindcss-animate`, `@tailwindcss/typography`) were in `devDependencies`. CI hosts run `npm ci` without `--include=dev` by default. The plugins are missing when PostCSS loads the Tailwind config.

### Fix
Move all Tailwind plugins used at build time to `dependencies`:
```json
{
  "dependencies": {
    "tailwindcss": "^3.4.0",
    "tailwindcss-animate": "^1.0.7",
    "@tailwindcss/typography": "^0.5.15"
  }
}
```

**Rule:** If a package is `require()`d inside `tailwind.config.js` or `postcss.config.js`, it must be in `dependencies`.

---

## Pitfall 3 — @tailwindcss/vite conflicts with Tailwind v3

### Symptom
Build crashes in vite:css transform. May look similar to Pitfall 1.

### Root Cause
`@tailwindcss/vite` is the Vite plugin for Tailwind **v4**. Installing it alongside Tailwind v3 (even if unused, not imported in `vite.config.ts`) pulls in a v4 engine. The v4 engine does not understand `@tailwind base/components/utilities` directives used by v3.

### Fix
Remove `@tailwindcss/vite` entirely from `package.json`. Verify it is not imported anywhere:
```bash
grep -r "@tailwindcss/vite" . --include="*.ts" --include="*.js" | grep -v node_modules
```
If the output is empty, it was unused. Delete it and regenerate the lock file.

---

## Pitfall 4 — tsx not found (npm overrides corrupt .bin symlink)

### Symptom
```
sh: 1: tsx: not found
```
Build script: `tsx script/build.ts`

### Root Cause
npm `overrides` can redirect package resolutions in ways that corrupt the `.bin/tsx` symlink. For example, aliasing `@esbuild-kit/esm-loader → tsx` for drizzle-kit causes the `.bin/tsx` symlink to point to the wrong location. The shell cannot execute it.

### Fix
Bypass the `.bin` symlink entirely by calling tsx's CJS entry point directly:
```json
{ "scripts": { "build": "node node_modules/tsx/dist/cli.cjs script/build.ts" } }
```
This works regardless of symlink state because it resolves the module path via Node's module system, not the shell's PATH.

**Do not** move `tsx` between `dependencies` and `devDependencies` to fix this — that changes the lock file without fixing the symlink root cause.

---

## Pitfall 5 — Lock file out of sync

### Symptom
```
npm ERR! Missing: @esbuild-kit/esm-loader@...
npm ERR! Lock file is out of sync with package.json
```

### Root Cause
`package.json` was modified (adding/removing packages, adding/removing `overrides`) without regenerating `package-lock.json`. `npm ci` requires the lock file to match exactly — it does not update it.

### Fix
After **every** `package.json` change, run:
```bash
npm install --package-lock-only   # regenerates lock without installing
npm ci --dry-run                  # verify it will pass
git add package.json package-lock.json
git commit -m "chore: sync lock file"
```

**Both files must always be committed together.**

---

## Pitfall 6 — Node version below framework minimum

### Symptom
Build exits with status 1, no error output, or a cryptic internal Node error.

### Root Cause
Vite 7 requires `^20.19.0 || >=22.12.0`. CI hosts that resolve `20` or `node:20` to whatever 20.x is available on their platform may pick 20.11.x or 20.18.x — both below the 20.19.0 floor. The build fails before producing useful output.

### Fix
Pin Node version explicitly in all three places:

```
# .node-version (committed to repo)
20.19.0
```
```json
// package.json
{ "engines": { "node": "^20.19.0 || >=22.12.0" } }
```
```yaml
# render.yaml
services:
  - nodeVersion: 20.19.0
```

---

## Pitfall 7 — VITE_ env vars not visible to server at runtime

### Symptom
```
Error: supabaseUrl is required.
    at validateSupabaseUrl (...)
```
Even though env vars are set in the Render dashboard.

### Root Cause
The convention `VITE_SUPABASE_URL` is a **naming choice** made when setting up the Render dashboard variables. There is no magic — the server process receives exactly the variable names that were set. If the server code reads `process.env.SUPABASE_URL` but the dashboard has `VITE_SUPABASE_URL`, they do not match.

`VITE_` prefix has special meaning only during the **Vite build** (Vite inlines `VITE_*` vars into the frontend bundle). At runtime, the server process sees all env vars as-is.

### Fix
Make the server read both names:
```typescript
const supabaseUrl =
  process.env.SUPABASE_URL ||
  process.env.VITE_SUPABASE_URL ||
  '';

const supabaseKey =
  process.env.SUPABASE_ANON_KEY ||
  process.env.VITE_SUPABASE_ANON_KEY ||
  '';

if (!supabaseUrl || !supabaseKey) {
  console.warn('[supabase] Missing credentials — check env vars');
}
```

Or, standardize on one naming convention and use it consistently in both the dashboard and server code.

---

## Quick Diagnosis Table

| Log pattern | Pitfall | Fix |
|-------------|---------|-----|
| CSS content dumped, `vite:css` crash | 1 — tailwind.config.ts + jiti v2 | Rename to `.js`, use `module.exports` |
| `Cannot find module '@tailwindcss/...'` | 2 — plugin in devDeps | Move to `dependencies` |
| vite:css crash, `@tailwindcss/vite` installed | 3 — v4 plugin conflict | Remove `@tailwindcss/vite` |
| `tsx: not found` | 4 — .bin symlink corrupted | Use `node node_modules/tsx/dist/cli.cjs` |
| `Lock file out of sync` | 5 — package.json changed without lock regen | `npm install --package-lock-only` |
| Silent exit, no error | 6 — Node version too old | Pin `nodeVersion: 20.19.0` |
| `supabaseUrl is required` at startup | 7 — env var name mismatch | Read both `X` and `VITE_X` names |

## Pre-Deploy Checklist

Before pushing to a CI/CD host for the first time:

- [ ] `tailwind.config.js` (not `.ts`)
- [ ] No `@tailwindcss/vite` in package.json
- [ ] All Tailwind plugins in `dependencies` (not devDeps)
- [ ] `.node-version` file pinned to exact version (e.g. `20.19.0`)
- [ ] `nodeVersion` set in `render.yaml` (or equivalent)
- [ ] `npm install --package-lock-only` run after last `package.json` change
- [ ] `rm -rf node_modules && npm ci && npm run build` passes locally
- [ ] Server reads both `process.env.X || process.env.VITE_X` for any var that might have either name
