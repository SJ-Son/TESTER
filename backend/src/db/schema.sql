-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Generation History Table
create table public.generation_history (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete set null,
  input_code text not null,
  language varchar(50) not null,
  model varchar(50) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- RLS (Row Level Security) Policies
alter table public.generation_history enable row level security;

-- Index for performance (Filtering by user and sorting by date is common)
create index if not exists generation_history_user_id_idx on public.generation_history (user_id);
create index if not exists generation_history_created_at_idx on public.generation_history (created_at desc);

-- 1. Policy: Users can only see their own history
create policy "Users can view own history"
on public.generation_history for select
to authenticated
using (auth.uid() = user_id);

-- 2. Policy: Users can only insert their own history
create policy "Users can insert own history"
on public.generation_history for insert
to authenticated
with check (auth.uid() = user_id);

-- 3. Policy: Users can only delete their own history
create policy "Users can delete own history"
on public.generation_history for delete
to authenticated
using (auth.uid() = user_id);

-- 4. Policy: Protect against updates (History is usually immutable)
-- No UPDATE policy means updates are denied by default.

