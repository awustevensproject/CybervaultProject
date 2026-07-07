create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  username text unique not null,
  email text unique not null,
  password_hash text not null,
  role text not null default 'user',
  created_at timestamptz not null default now()
);

alter table public.users enable row level security;
