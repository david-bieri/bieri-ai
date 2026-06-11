---
name: supabase-app
description: "Design, migrate, and manage Supabase PostgreSQL schemas for full-stack web apps. Use when building or evolving a Supabase-backed application. Covers defining tables with RLS, writing migration SQL, applying migrations via the Perplexity Supabase connector, generating TypeScript types, handling env configuration, and implementing real-time sync. Covers free-tier constraints, index design, and migration workflow."
version: "1.1"
---

# webdev:supabase-app
_v1.1 — platform-agnostic; adds connector migration pattern_

Design, migrate, and manage Supabase PostgreSQL schemas for full-stack web apps.

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
  process.env.SUPABASE_URL!,       // server-side
  process.env.SUPABASE_ANON_KEY!
);

// OR in a Vite frontend (public env vars):
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);
```

Environment variables:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJ...
# Vite frontend prefix:
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

If the same app uses both prefixes (e.g. a server that might receive either), read defensively:
```typescript
const url  = process.env.SUPABASE_URL  || process.env.VITE_SUPABASE_URL;
const key  = process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY;
```

### Step 2 — Schema design

Standard column patterns:
```sql
id         text    primary key,                              -- app-generated (nanoid/uuid/cuid)
-- OR:
id         uuid    default gen_random_uuid() primary key,   -- Supabase-generated
created_at timestamptz default now(),
updated_at timestamptz default now(),
assignees  text[],   -- multi-person array
status     text check (status in ('pending','active','completed','cancelled'))
```

Always index columns used in `WHERE` or `ORDER BY`:
```sql
-- Index on a foreign key:
create index if not exists idx_items_user_id on items(user_id);
-- Index on a date column used for sorting/filtering:
create index if not exists idx_items_date on items(date);
-- Index on a lookup column (e.g. dedup key):
create index if not exists idx_items_external_id on items(external_id);
```

### Step 3 — Migrations

Structure every migration as idempotent SQL so it can be re-run safely:
```sql
-- migrations/001_description.sql
create table if not exists my_table (
  id           text primary key,
  name         text not null,
  created_at   timestamptz default now()
);

create index if not exists idx_my_table_name on my_table(name);

alter table my_table enable row level security;

-- Open policy (adjust to your auth model):
create policy if not exists "public_all" on my_table
  for all using (true) with check (true);

-- Seed data (idempotent):
insert into my_table (id, name) values
  ('seed-1', 'Default Item')
on conflict do nothing;
```

**How to apply migrations — three options:**

Option A — Perplexity Supabase connector (when running inside a Perplexity agent session):
```
call_external_tool(
  tool_name="apply_migration",
  source_id="supabase",
  arguments={
    "project_id": "your-project-ref",   // 20-char ref from your Supabase project URL
    "name": "snake_case_migration_name",
    "query": "<full idempotent SQL>"
  }
)
```

Option B — Supabase Dashboard: Project → SQL Editor → paste and run.

Option C — CLI / psql:
```bash
psql "$DATABASE_URL" -f migrations/001_description.sql
# or via supabase CLI:
supabase db push
```

### Step 4 — Real-time subscriptions

```typescript
const channel = supabase
  .channel('my-table-changes')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'my_table' },
    (payload) => {
      // update local state with payload.new / payload.old
    }
  )
  .subscribe();

// Clean up on component/module teardown:
return () => supabase.removeChannel(channel);
```

Replication must be enabled on the table for real-time to fire (Supabase Dashboard → Database → Replication, or via SQL: `alter publication supabase_realtime add table my_table`).

---

## Free tier limits

| Limit | Value |
|-------|-------|
| Database size | 500 MB |
| Monthly active users | 50,000 |
| Bandwidth | 5 GB |
| Realtime connections | 200 concurrent |

Staying within limits: select only needed columns, prefer soft-delete over hard-delete, batch inserts, use real-time subscriptions instead of polling.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 401 Unauthorized | Anon key doesn't match project |
| RLS blocks reads | Add `for select using (true)` policy |
| Duplicate key on import | Use `on conflict do nothing` |
| Real-time not firing | Enable table replication |
| Slow queries | Add index on filter/sort columns |
| `supabaseUrl is required` | Server is reading bare `SUPABASE_URL` but env has `VITE_SUPABASE_URL` — add fallback: `process.env.SUPABASE_URL \|\| process.env.VITE_SUPABASE_URL` |
| Migration fails on re-run | Not idempotent — add `if not exists` to `create table/index`, `on conflict` to inserts |

---

## QA checklist

- [ ] All tables have `id` PK and `created_at timestamptz`
- [ ] RLS enabled on every table (`alter table t enable row level security`)
- [ ] Indexes on FK and date/filter columns
- [ ] Migration runs idempotently (`if not exists`, `on conflict do nothing`)
- [ ] `.env` file is in `.gitignore` — credentials never committed
- [ ] Server reads both `SUPABASE_URL` and `VITE_SUPABASE_URL` defensively if env name may vary
- [ ] Real-time tables added to `supabase_realtime` publication if subscriptions are used
