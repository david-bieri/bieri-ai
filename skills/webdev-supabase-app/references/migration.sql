-- migration.sql — Reference multi-table schema
-- Demonstrates: uuid PKs, timestamptz, arrays, enums, RLS, indexes, seed data
-- Adapt table names and columns for your domain.

-- ── Core: Events ─────────────────────────────────────────────────────────────
create table if not exists events (
  id           uuid    default gen_random_uuid() primary key,
  title        text    not null,
  description  text,
  date         date,
  end_date     date,
  time         text,
  category     text    not null default 'other',
  assignees    text[], -- array of names/IDs
  recurrence   text    not null default 'none'
                check (recurrence in ('none','daily','weekly')),
  recurrence_end_date date,
  amount       numeric(10,2),
  status       text    default 'active'
                check (status in ('active','completed','cancelled','pending')),
  source       text    default 'manual', -- 'manual'|'email'|'import'
  gmail_id     text,   -- deduplication key for email-sourced events
  notes        text,
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

create index if not exists idx_events_category on events(category);
create index if not exists idx_events_date     on events(date);
create index if not exists idx_events_gmail_id on events(gmail_id);

-- ── Categories ────────────────────────────────────────────────────────────────
create table if not exists categories (
  id         uuid default gen_random_uuid() primary key,
  name       text unique not null,
  color      text not null default '#6b7280',
  icon       text,
  is_default boolean default false,
  created_at timestamptz default now()
);

-- ── Pending Imports (email inbox staging) ─────────────────────────────────────
create table if not exists pending_imports (
  id         uuid default gen_random_uuid() primary key,
  gmail_id   text unique not null,
  subject    text,
  from_addr  text,
  date       text,
  snippet    text,
  body       text,
  parsed     jsonb,  -- tag-parser output
  status     text default 'pending'
              check (status in ('pending','approved','rejected','auto-imported')),
  created_at timestamptz default now()
);

create index if not exists idx_pending_imports_gmail_id on pending_imports(gmail_id);
create index if not exists idx_pending_imports_status  on pending_imports(status);

-- ── Share Tokens (read-only public calendar links) ────────────────────────────
create table if not exists share_tokens (
  id         uuid default gen_random_uuid() primary key,
  token      text unique not null,
  label      text,
  expires_at timestamptz,
  created_at timestamptz default now()
);

-- ── Vaccines (human) ──────────────────────────────────────────────────────────
create table if not exists vaccines (
  id           uuid default gen_random_uuid() primary key,
  person_name  text not null,
  vaccine_name text not null,
  status       text default 'scheduled'
                check (status in ('completed','scheduled','overdue','not_required','declined')),
  due_date     date,
  completed_date date,
  notes        text,
  created_at   timestamptz default now()
);

-- ── Pets ──────────────────────────────────────────────────────────────────────
create table if not exists pets (
  id         uuid default gen_random_uuid() primary key,
  name       text not null,
  species    text,  -- 'dog'|'cat'|'other'
  breed      text,
  color      text  default '#78716c',
  birthdate  date,
  notes      text,
  created_at timestamptz default now()
);

create table if not exists pet_vaccines (
  id           uuid default gen_random_uuid() primary key,
  pet_id       uuid references pets(id) on delete cascade,
  vaccine_name text not null,
  status       text default 'scheduled'
                check (status in ('completed','scheduled','overdue','not_required','declined')),
  due_date     date,
  completed_date date,
  notes        text,
  created_at   timestamptz default now()
);

-- ── RLS Policies (public app — single-password auth) ─────────────────────────
do $$ 
declare t text;
begin
  for t in select unnest(array[
    'events','categories','pending_imports','share_tokens',
    'vaccines','pets','pet_vaccines'
  ]) loop
    execute format('alter table %I enable row level security', t);
    execute format(
      'create policy "public_all" on %I for all using (true) with check (true)', t
    );
  end loop;
end $$;

-- ── Seed Data ─────────────────────────────────────────────────────────────────
insert into categories (name, color, is_default) values
  ('school',  '#3b82f6', true),
  ('sports',  '#22c55e', true),
  ('medical', '#ef4444', true),
  ('camp',    '#f59e0b', true),
  ('family',  '#8b5cf6', true),
  ('payment', '#f97316', true),
  ('other',   '#6b7280', true),
  ('pets',    '#78716c', false)
on conflict (name) do nothing;
