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
