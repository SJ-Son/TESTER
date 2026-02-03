-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Test Generation Logs Table
create table public.test_logs (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete set null,
  input_code text not null,
  language varchar(50) not null,
  model varchar(50) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- RLS (Row Level Security) Policies
alter table public.test_logs enable row level security;

-- Index for performance (Filtering by user and sorting by date is common)
create index if not exists test_logs_user_id_idx on public.test_logs (user_id);
create index if not exists test_logs_created_at_idx on public.test_logs (created_at desc);

-- 1. Policy: Users can only see their own logs
create policy "Users can view own logs"
on public.test_logs for select
to authenticated
using (auth.uid() = user_id);

-- 2. Policy: Users can only insert logs for themselves
create policy "Users can insert own logs"
on public.test_logs for insert
to authenticated
with check (auth.uid() = user_id);

-- 3. Policy: Users can only delete their own logs
create policy "Users can delete own logs"
on public.test_logs for delete
to authenticated
using (auth.uid() = user_id);

-- 4. Policy: Protect against updates (Logs are usually immutable in production)
-- No UPDATE policy means updates are denied by default, which is safer for logs.

