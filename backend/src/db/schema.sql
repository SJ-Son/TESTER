-- Drop table if exists to allow clean recreate (Caution: Data loss!)
drop table if exists public.generation_history;

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Generation History Table
create table public.generation_history (
  id uuid default uuid_generate_v4() primary key,
  user_id text not null, -- Changed from UUID to TEXT for Google ID, removed FK
  input_code text not null,
  generated_code text not null,
  language varchar(50) not null,
  model varchar(50) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Index for performance (Filtering by user and sorting by date is common)
create index if not exists generation_history_user_id_idx on public.generation_history (user_id);
create index if not exists generation_history_created_at_idx on public.generation_history (created_at desc);

-- RLS Removed: Backend manages access via Service Role Key


