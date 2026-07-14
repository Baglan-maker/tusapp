# Түс (Tús)

Voice dream journal with AI interpretation for the CIS / Kazakhstan market (ru, kk).

Monorepo:

- `apps/api` — FastAPI backend (Python 3.12, uv, SQLAlchemy 2.0, Alembic).
- `apps/mobile` — Expo (React Native + TypeScript) client.

See [CLAUDE.md](CLAUDE.md) for conventions and [tus-strategy.md](tus-strategy.md) for the full plan.

## Local development

Prerequisites: [uv](https://docs.astral.sh/uv/), Docker, Node 20+.

```bash
# 1. Start local Postgres + pgvector
docker compose up -d

# 2. Backend
cd apps/api
cp ../../.env.example .env        # fill in keys as needed
uv sync
uv run alembic upgrade head
uv run python -m app.seeds.symbols
uv run python -m app.seeds.emotions
uv run uvicorn app.main:app --reload
# -> http://127.0.0.1:8000/health

# 3. Mobile (separate terminal)
cd apps/mobile
npm install
npx expo start
```

## Deployment

**Supabase** (Postgres + Auth)

1. Create the project. Copy the connection string into `DATABASE_URL`, switching the
   driver: `postgresql+psycopg://…`.
2. Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`. The API verifies client JWTs against
   `$SUPABASE_URL/auth/v1/.well-known/jwks.json`.
3. Enable the auth providers (Apple / Google / email).
4. Apply row-level security **once** — it is deliberately not in the Alembic chain,
   because `auth.uid()` does not exist in local/CI Postgres:
   ```bash
   psql "$SUPABASE_DB_URL" -f supabase/rls.sql
   ```
   RLS is defense-in-depth only: the API connects with the service key (which bypasses
   RLS) and is the real authorization boundary.

**Railway** (API)

1. New service from this repo, **root directory `apps/api`** — it builds the Dockerfile.
2. Set the env vars from [.env.example](.env.example) (DB, Supabase, AI keys).
3. Add repo secrets `RAILWAY_TOKEN` and `RAILWAY_SERVICE`. The `deploy` job in
   [CI](.github/workflows/ci.yml) runs on `main` **only after lint, typecheck and tests
   are green**.
4. Migrations need no separate step: the container runs `alembic upgrade head` on boot.
