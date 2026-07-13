"""Run the golden dreams through the REAL pipeline and write a Markdown report.

This is the only place that makes real AI calls — tests always mock. Use it to
eyeball interpretation quality per model:

    uv run python -m scripts.eval_golden --model claude-haiku-4-5 --out eval_reports/haiku.md
    uv run python -m scripts.eval_golden --model claude-sonnet-5  --out eval_reports/sonnet.md

Reads base lens meanings from the DB read-only (needs `docker compose up -d`);
persists nothing. User history is empty by design — golden dreams stand alone.
"""

import argparse
import json
from pathlib import Path

from app.config import settings
from app.db import SessionLocal
from app.models.symbol import Symbol
from app.prompts import Lens
from app.schemas.extraction import DreamExtraction
from app.services import llm

# $ per 1M tokens (input, output) — for a rough cost line in the report.
PRICING: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-opus-4-8": (5.0, 25.0),
}

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "tests" / "golden" / "dreams.json"


def _meanings(slugs: list[str], lens: Lens) -> dict[str, str]:
    if not slugs:
        return {}
    out: dict[str, str] = {}
    with SessionLocal() as session:
        rows = session.query(Symbol.slug, Symbol.lens_meanings).filter(Symbol.slug.in_(slugs))
        for slug, lens_meanings in rows:
            value = (lens_meanings or {}).get(lens.value)
            if value:
                out[slug] = value
    return out


def _symbols_line(extraction: DreamExtraction) -> str:
    return ", ".join(f"{s.slug}: {s.salience:.2f}" for s in extraction.symbols)


def _emotions_line(extraction: DreamExtraction) -> str:
    return ", ".join(f"{e.slug} ({e.kind})" for e in extraction.emotions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=settings.interpret_model)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    settings.interpret_model = args.model  # llm.interpret reads this
    out_path = Path(args.out or f"eval_reports/{args.model}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dreams = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if not dreams:
        print(f"No golden dreams in {GOLDEN_PATH} — drop your file there first.")
        return

    lines: list[str] = [f"# Golden eval — `{args.model}`\n"]
    total_in = total_out = 0

    for dream in dreams:
        language = dream["language"]
        transcript = dream["transcript"]
        lens = Lens(dream.get("lens", "psych"))

        extraction = llm.extract(transcript, language)
        meanings = _meanings([s.slug for s in extraction.symbols], lens)
        result = llm.interpret(
            language=language,
            lens=lens,
            symbols_line=_symbols_line(extraction),
            meanings_block="\n".join(f"- {k}: {v}" for k, v in meanings.items()),
            emotions_line=_emotions_line(extraction),
            recent_block="",
            patterns_block="",
            transcript=transcript,
        )
        total_in += result.tokens_in
        total_out += result.tokens_out

        lines += [
            f"## {dream.get('id', '?')} — {language} / {lens.value}\n",
            f"**Сон:** {transcript}\n",
            f"**Символы:** {_symbols_line(extraction) or '—'}",
            f"**Эмоции:** {_emotions_line(extraction) or '—'}",
            f"**Токены:** in {result.tokens_in} / out {result.tokens_out}\n",
            "**Толкование:**\n",
            result.content_md,
            "\n---\n",
        ]

    price_in, price_out = PRICING.get(args.model, (0.0, 0.0))
    cost = total_in / 1e6 * price_in + total_out / 1e6 * price_out
    lines.append(
        f"**Итого:** in {total_in} / out {total_out} токенов · "
        f"≈ ${cost:.4f} за {len(dreams)} снов ({args.model})\n"
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path} — {len(dreams)} dreams, ${cost:.4f}.")


if __name__ == "__main__":
    main()
