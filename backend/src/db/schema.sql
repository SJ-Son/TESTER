-- Drop table if exists to allow clean recreate (Caution: Data loss!)
drop table if exists public.generation_history;

-- Enable Extensions
create extension if not exists "uuid-ossp";
create extension if not exists vector;

-- Generation History Table
create table public.generation_history (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete set null, -- Restored to UUID and FK
  input_code text not null,
  generated_code text not null,
  language varchar(50) not null,
  model varchar(50) not null,
  status varchar(20) default 'success' not null,
  source_code_embedding vector(768),
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

-- 4. Vector index for fast similarity search
create index if not exists generation_history_embedding_idx on public.generation_history using hnsw (source_code_embedding vector_cosine_ops);

-- RCP for finding similar successful generations (Few-shot prompting)
create or replace function public.match_successful_generations(
  query_embedding vector(768),
  match_limit int,
  p_language varchar default null
)
returns table (
  input_code text,
  generated_code text,
  similarity float
)
language sql stable
as $$
  select
    input_code,
    generated_code,
    1 - (source_code_embedding <=> query_embedding) as similarity
  from public.generation_history
  where status = 'success'
  and source_code_embedding is not null
  and (p_language is null or language = p_language)
  order by source_code_embedding <=> query_embedding
  limit match_limit;
$$;
