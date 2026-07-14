# Түс (Tús) — monorepo

Voice dream journal with AI interpretation for the CIS / Kazakhstan market (ru, kk).
Solo founder, side-project, built iteratively with Claude Code.

Full product & business strategy: [tus-strategy.md](tus-strategy.md).

## Layout

```
apps/api      FastAPI (Python 3.12, uv, SQLAlchemy 2.0, Alembic, pytest) — the only backend "brain"
apps/mobile   Expo (React Native + TypeScript) — mobile client
docker-compose.yml   local Postgres 16 + pgvector
```

Supabase provides Postgres + Auth + Storage in production. The mobile client
authenticates with Supabase and calls FastAPI with the Supabase JWT; FastAPI
verifies the JWT and owns all business logic. Supabase RLS is defense-in-depth,
**not** the primary authorization — FastAPI is.

## Stack decisions (agreed — do not change without discussion)

- STT routing by language: **ru → Groq whisper-large-v3**, **kk → ElevenLabs Scribe**
  (vanilla Whisper is unusable on Kazakh). Always show an **editable transcript**
  before interpretation.
- LLM: Anthropic — Haiku for free tier, Sonnet for premium.
- Embeddings: OpenAI `text-embedding-3-small` (1536) → pgvector.
- Scheduler: APScheduler in-process / pg_cron. **No Celery.**
- Audio is **deleted after successful transcription** by default (privacy + storage).
- No `packages/shared` / OpenAPI type-gen yet (premature).

## Design tokens (apps/mobile) — "Предрассветный час"

Reference mock: [tus-ui-v2.html](tus-ui-v2.html). Dark theme is the **only** theme.

```
Background   linear-gradient 178deg  #221A4A → #120D2C (52%) → #0F0B22
Surfaces     rgba(46,37,89,.38) · border rgba(167,155,200,.16) · blur 6
Accent       GOLD ONLY — #F6E9CC (champagne) → #E9C87E (gold) → #CEA45A (gold-deep)
Text         #F5F2FB (dawn) · secondary #A79BC8 (lilac) · dim #7B6FA0
Radii        cards 24 · buttons 28 (height 56) · chips 18 · tags 14
Fonts        display = Alice (400 only — no bold display) — LARGE HEADINGS ONLY
             Manrope 400–800 — everything else
Atmosphere   nebula glows, twinkling stars, film grain (opacity .05)
Moon button  176px · breathe 4.2s · scale 1 → 1.045
```

**Hard rules:** no neon. No emoji in the UI — line SVG icons only (stroke 1.6–2).
Honor `prefers-reduced-motion` / `AccessibilityInfo.isReduceMotionEnabled` — kill
the breathing and twinkling when it is on.

## Conventions

- **Code and comments in English.** UI strings go through i18n (ru/kk); en keys later.
- **One vertical slice per session.** Skeleton first, then record → STT → interpret, etc.
- **Secrets only via env.** Keep `.env.example` in sync; never commit real keys.
- **Every endpoint** has explicit Pydantic request/response schemas.
- **Tests are mandatory for business logic** (quota, pipeline, pattern engine).
- **All AI calls**: timeout + exponential-backoff retry + log `tokens_in`/`tokens_out`
  into `interpretations`.
- **User upsert from JWT**: reject a missing/empty `sub` claim (see `app/auth.py`).
- Enum-like columns are `text` + `CHECK` constraints (not native PG enums).
- `usage_quota` has a composite PK `(user_id, day)`; `dreams` use soft delete (`deleted_at`).

## apps/api — common commands

```bash
cd apps/api
uv sync                      # install deps (incl. dev)
uv run alembic upgrade head  # apply migrations
uv run python -m app.seeds.symbols    # seed 30 dream symbols (idempotent)
uv run python -m app.seeds.emotions   # seed emotions reference (idempotent)
uv run uvicorn app.main:app --reload  # run API
uv run pytest                # tests
uv run ruff check . && uv run ruff format --check . && uv run mypy app
```

Local DB: `docker compose up -d` from repo root first.
