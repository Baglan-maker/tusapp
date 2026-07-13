# Golden dreams

`dreams.json` is a **stub** — drop your own set here (the messy, fragmentary ones).

Expected shape: a JSON array of objects.

```json
[
  {
    "id": "ru-1",
    "language": "ru",
    "transcript": "…текст сна…",
    "lens": "psych"
  }
]
```

- `id` — any stable string (used in the report).
- `language` — `ru` or `kk`.
- `transcript` — the dream text.
- `lens` — optional, one of `psych | classic | ibn_sirin | science` (default `psych`).

Run the eval (real API calls — needs keys in `.env`):

```bash
uv run python -m scripts.eval_golden --model claude-haiku-4-5 --out eval_reports/haiku.md
uv run python -m scripts.eval_golden --model claude-sonnet-5  --out eval_reports/sonnet.md
```

Then eyeball the two Markdown reports side by side.
