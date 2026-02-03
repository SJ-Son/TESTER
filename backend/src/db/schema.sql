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

-- Policy: Users can insert their own logs
create policy "Users can insert their own logs"
on public.test_logs for insert
with check (auth.uid() = user_id);

-- Policy: Users can view their own logs
create policy "Users can view their own logs"
on public.test_logs for select
using (auth.uid() = user_id);
