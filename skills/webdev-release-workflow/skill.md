# webdev:release-workflow

This skill is an **orchestrator**. It defines the sequence of steps for releasing a web project but delegates implementation details to specialized domain skills. Do not duplicate content from those skills here — read and invoke them at the appropriate step.

## The Release Sequence

When asked to merge a development branch into production, follow these steps in order:

```
Step 1: Smoke Test ──────────► cross-browser-smoke-test
Step 2: Documentation Sync ──► latex-pdf-guide + static-site-i18n
Step 3: Merge & Push
Step 4: Deploy Verification ─► static-site-i18n (concurrency handling)
Step 5: Post-Merge Hotfixes ─► static-site-i18n + contact-protocol-links (if applicable)
```

---

### Step 1: Smoke Test

Read and follow the `cross-browser-smoke-test` skill. Produce a smoke test report. If the report concludes with a FAIL verdict, stop the release and fix the issues before continuing.

### Step 2: Documentation Sync

Before merging, ensure documentation matches the current feature set:

1. Compare the live UI against the existing docs to identify undocumented features.
2. If the project uses LaTeX guides, read and follow the `latex-pdf-guide` skill (Section 4: Syncing Rule).
3. Update `README.md` to reflect any new files, architecture changes, or features.
4. Commit all documentation updates to the **development branch** before merging.

### Step 3: Merge & Push

Execute the merge preserving branch history:

```bash
git checkout main
git merge dev --no-ff -m "Merge dev into main: <descriptive release title>"
git push origin main
```

### Step 4: Deploy Verification

If the project deploys via GitHub Actions (or similar CI/CD), confirm the deployment succeeds. For race condition handling, refer to `static-site-i18n` (Section 3: Concurrency Handling).

### Step 5: Post-Merge Hotfixes

Users often request minor fixes immediately after a release. When applying hotfixes to `main`:

1. Read `static-site-i18n` for the propagation rule (grep all `.html` files, update `strings.js`).
2. If the fix involves contact information, read `contact-protocol-links` for the correct protocol link format.
3. Commit atomically and push. Inform the user a new deployment has been triggered.

---

## Related Skills

| Step | Skill to Read | What It Provides |
|------|---------------|-----------------|
| 1 | `cross-browser-smoke-test` | Testing methodology, checklist, report template |
| 2 | `latex-pdf-guide` | LaTeX compilation, PDF web delivery, syncing rule |
| 2, 5 | `static-site-i18n` | i18n string updates, footer propagation, deployment concurrency |
| 5 | `contact-protocol-links` | Protocol link formats (mailto, tel, sms, wa.me) |
| 2 | `d3-analytics-modules` | Tab-mounted module conventions (if analytics features changed) |
| 2 | `json-data-enrichment` | Data schema migrations (if JSON data fields changed) |
