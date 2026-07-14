-- Row Level Security — DEFENSE IN DEPTH ONLY.
--
-- The API is the primary authorization boundary: it verifies the Supabase JWT,
-- takes user_id from the token, and scopes every query. It connects with the
-- service key, which BYPASSES RLS. These policies exist so that any *direct*
-- client access to Postgres (now or later) can only ever see its own rows.
--
-- This file is NOT part of the Alembic chain on purpose: auth.uid() does not
-- exist in local/CI Postgres, so putting it in a migration would break both.
--
-- Apply once to the Supabase project:
--   psql "$SUPABASE_DB_URL" -f supabase/rls.sql
-- (or paste into the Supabase SQL editor)

-- ---------------------------------------------------------------- user-owned
alter table users          enable row level security;
alter table profiles       enable row level security;
alter table dreams         enable row level security;
alter table patterns       enable row level security;
alter table streaks        enable row level security;
alter table subscriptions  enable row level security;
alter table usage_quota    enable row level security;

create policy users_self on users
  for all using (id = auth.uid()) with check (id = auth.uid());

create policy profiles_self on profiles
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy dreams_self on dreams
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy patterns_self on patterns
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy streaks_self on streaks
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy subscriptions_self on subscriptions
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy usage_quota_self on usage_quota
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- ------------------------------------------------------------- dream-derived
alter table interpretations   enable row level security;
alter table dream_symbols     enable row level security;
alter table dream_emotions    enable row level security;
alter table dream_embeddings  enable row level security;
alter table share_cards       enable row level security;

create policy interpretations_own_dream on interpretations
  for all using (
    exists (select 1 from dreams d where d.id = dream_id and d.user_id = auth.uid())
  );

create policy dream_symbols_own_dream on dream_symbols
  for all using (
    exists (select 1 from dreams d where d.id = dream_id and d.user_id = auth.uid())
  );

create policy dream_emotions_own_dream on dream_emotions
  for all using (
    exists (select 1 from dreams d where d.id = dream_id and d.user_id = auth.uid())
  );

create policy dream_embeddings_own_dream on dream_embeddings
  for all using (
    exists (select 1 from dreams d where d.id = dream_id and d.user_id = auth.uid())
  );

create policy share_cards_own_dream on share_cards
  for all using (
    exists (select 1 from dreams d where d.id = dream_id and d.user_id = auth.uid())
  );

-- ------------------------------------------------- public reference data (RO)
alter table symbols   enable row level security;
alter table emotions  enable row level security;

create policy symbols_read on symbols
  for select to authenticated using (true);

create policy emotions_read on emotions
  for select to authenticated using (true);
