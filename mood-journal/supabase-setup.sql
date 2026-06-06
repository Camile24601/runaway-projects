create table if not exists public.mood_entries (
  journal_key text not null,
  entry_date date not null,
  mood text not null,
  icon text not null,
  body text default '',
  image text default '',
  updated_at timestamptz default now(),
  primary key (journal_key, entry_date)
);

alter table public.mood_entries enable row level security;

drop policy if exists "mood entries can be read" on public.mood_entries;
drop policy if exists "mood entries can be inserted" on public.mood_entries;
drop policy if exists "mood entries can be updated" on public.mood_entries;
drop policy if exists "mood entries can be deleted" on public.mood_entries;

create policy "mood entries can be read"
on public.mood_entries
for select
to anon
using (true);

create policy "mood entries can be inserted"
on public.mood_entries
for insert
to anon
with check (true);

create policy "mood entries can be updated"
on public.mood_entries
for update
to anon
using (true)
with check (true);

create policy "mood entries can be deleted"
on public.mood_entries
for delete
to anon
using (true);
