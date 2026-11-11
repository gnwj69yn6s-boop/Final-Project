create extension if not exists vector;

create table users (
  id uuid primary key default gen_random_uuid(),
  nickname text not null,
  notify_email text,
  consent_at timestamptz not null,
  created_at timestamptz default now()
);

create table recipes (
  id bigserial primary key,
  title text not null,
  ingredients text[] not null,
  steps text not null,
  time_min int,
  difficulty text,
  embedding vector(512)
);

create table memories (
  id bigserial primary key,
  user_id uuid references users(id) on delete cascade,
  kind text check (kind in ('allergy','dislike','diet','skill','note')),
  content text not null,
  created_at timestamptz default now()
);

create table messages (
  id bigserial primary key,
  user_id uuid references users(id) on delete cascade,
  role text check (role in ('user','assistant')),
  content text not null,
  created_at timestamptz default now()
);

create table shopping_items (
  id bigserial primary key,
  user_id uuid references users(id) on delete cascade,
  item text not null,
  done boolean default false,
  created_at timestamptz default now()
);

create table feedback (
  id bigserial primary key,
  user_id uuid references users(id) on delete cascade,
  message_id bigint,
  rating int check (rating in (-1, 1)),
  comment text,
  created_at timestamptz default now()
);

create index on recipes using hnsw (embedding vector_cosine_ops);

create or replace function match_recipes(
  query_embedding vector(512), match_count int, max_time int default null
) returns table (
  id bigint, title text, ingredients text[], steps text,
  time_min int, difficulty text, similarity float
) language sql stable as $$
  select r.id, r.title, r.ingredients, r.steps, r.time_min, r.difficulty,
         1 - (r.embedding <=> query_embedding) as similarity
  from recipes r
  where max_time is null or r.time_min <= max_time
  order by r.embedding <=> query_embedding
  limit match_count;
$$;
