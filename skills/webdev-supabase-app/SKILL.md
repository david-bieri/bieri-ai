---
name: supabase-app
description: "Design, migrate, and manage Supabase PostgreSQL schemas for full-stack web apps. Use when building or evolving a Supabase-backed application. Covers defining tables with RLS, writing migration SQL, applying migrations via the Perplexity Supabase connector, generating TypeScript types, handling env configuration, and implementing real-time sync. Covers free-tier constraints, index design, and migration workflow."
version: "1.1"
---

# webdev:supabase-app
_v1.1 — adds Perplexity connector migration pattern_

Design, migrate, and manage Supabase PostgreSQL schemas for full-stack web apps: table design with RLS, migration SQL, TypeScript client setup, real-time subscriptions, and free-tier constraints.

---

## When to invoke

Trigger on: "add a table to Supabase", "write the migration SQL", "set up RLS policies", "the Supabase query is failing", "add a real-time subscription", "generate TypeScript types", "set up the env vars for Supabase", or any schema design or database work on a Supabase-backed app.

---

## Workflow

### Step 1 — Client setup

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);
```

Environment variables (see `assets/.env.example`):
```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

### Step 2 — Schema design

Standard column patterns:
```sql
id         text    primary key,                              -- use nanoid() from server
-- OR:
id         uuid    default gen_random_uuid() primary key,   -- Supabase-generated
created_at timestamptz default now(),
updated_at timestamptz default now(),
assignees  text[],   -- multi-person arrays
recurrence text check (recurrence in ('none','daily','weekly')),
status     text check (status in ('pending','active','completed','cancelled'))
```

Always index FK columns and date columns used in `WHERE`:
```sql
create index if not exists idx_events_category on events(category);
create index if not exists idx_events_date     on events(date);
create index if not exists idx_pending_gmail   on pending_imports(gmail_id);
```

### Step 3 — Migrations

Structure every migration as idempotent SQL:
```sql
-- 001_description.sql
create table if not exists ... ;
create index if not exists ... ;
alter table ... enable row level security;
create policy "public_all" on ... for all using (true) with check (true);
insert into ... on conflict do nothing;  -- seed data
```

**Preferred: apply via Perplexity Supabase connector** (no dashboard needed):

```
call_external_tool(
  tool_name="apply_migration",
  source_id="supabase",
  arguments={
    "project_id": "your-project-id",
    "name": "snake_case_migration_name",
    "query": "<full SQL string>"
  }
)
```

Always call `describe_external_tools(source_id="supabase", tool_names=["apply_migration"])` first to confirm the schema, then pass the SQL as the `query` string value.

Alternative: Supabase Dashboard → SQL Editor, or `psql $DATABASE_URL -f migration.sql`.

See `references/migration.sql` for a complete multi-table example with RLS and seed data.

### Step 4 — Real-time subscriptions

```typescript
const channel = supabase
  .channel('table-changes')
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'events' },
    (payload) => { /* refresh local state */ }
  )
  .subscribe();

// Cleanup on component unmount
return () => supabase.removeChannel(channel);
```

---

## Free tier limits

| Limit | Value |
|-------|-------|
| Database size | 500 MB |
| Monthly active users | 50,000 |
| Bandwidth | 5 GB |
| Realtime connections | 200 concurrent |

Stay in free tier: use `select` with column lists, soft-delete instead of hard-delete, batch inserts, real-time over polling.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 Unauthorized | Anon key doesn't match project |
| RLS blocks reads | Add `for select using (true)` policy |
| Duplicate key on import | Add `on conflict do nothing` |
| Real-time not firing | Verify table has replication enabled |
| Slow queries | Add index on filter/sort columns |
| `supabaseUrl is required` | Server reads bare env var names; add `process.env.SUPABASE_URL \|\| process.env.VITE_SUPABASE_URL` fallback |

---

## QA checklist

- [ ] All tables have `id` PK and `created_at timestamptz`
- [ ] RLS enabled on every table
- [ ] Indexes on FK and date columns used in queries
- [ ] Migration runs idempotently (`if not exists`, `on conflict do nothing`)
- [ ] `.env` variables never committed (in `.gitignore`)
- [ ] Server reads `SUPABASE_URL || VITE_SUPABASE_URL` to handle both naming conventions
