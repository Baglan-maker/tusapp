"""Orchestrates the interpretation pipeline for one dream + lens."""

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.dream import Dream
from app.models.dream_embedding import DreamEmbedding
from app.models.dream_emotion import DreamEmotion
from app.models.dream_symbol import DreamSymbol
from app.models.emotion import Emotion
from app.models.interpretation import Interpretation
from app.models.symbol import Symbol
from app.prompts import Lens
from app.schemas.extraction import DreamExtraction
from app.services import context, embeddings, llm


def interpret_dream(session: Session, dream: Dream, lens: Lens) -> Interpretation:
    if not dream.transcript:
        raise ValueError("dream has no transcript to interpret")

    extraction = llm.extract(dream.transcript, dream.language or "ru")
    symbols = _persist_symbols(session, dream.id, extraction)
    _persist_emotions(session, dream.id, extraction)

    meanings = _lens_meanings(session, symbols, lens)
    ctx = context.build_context(session, dream.user_id, exclude_dream_id=dream.id)

    result = llm.interpret(
        language=dream.language or "ru",
        lens=lens,
        symbols_line=_symbols_line(extraction),
        meanings_block=_meanings_block(meanings),
        emotions_line=_emotions_line(extraction),
        recent_block=ctx.recent_block,
        patterns_block=ctx.patterns_block,
        transcript=dream.transcript,
    )

    _persist_embedding(session, dream.id, dream.transcript)

    interpretation = Interpretation(
        dream_id=dream.id,
        lens=lens.value,
        model=result.model,
        content_md=result.content_md,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
    )
    session.add(interpretation)
    session.commit()
    session.refresh(interpretation)
    return interpretation


def _persist_symbols(
    session: Session, dream_id: uuid.UUID, extraction: DreamExtraction
) -> dict[str, uuid.UUID]:
    """Upsert symbols by slug, link them to the dream, return {slug: symbol_id}."""
    slug_to_id: dict[str, uuid.UUID] = {}
    for item in extraction.symbols:
        symbol_id = _get_or_create_symbol(session, item.slug)
        slug_to_id[item.slug] = symbol_id
        session.execute(
            insert(DreamSymbol)
            .values(dream_id=dream_id, symbol_id=symbol_id, salience=item.salience)
            .on_conflict_do_update(
                index_elements=[DreamSymbol.dream_id, DreamSymbol.symbol_id],
                set_={"salience": item.salience},
            )
        )
    session.flush()
    return slug_to_id


def _get_or_create_symbol(session: Session, slug: str) -> uuid.UUID:
    existing = session.scalar(select(Symbol.id).where(Symbol.slug == slug))
    if existing is not None:
        return existing
    # New symbol discovered by the model: create a bare row (names/meanings
    # enriched later out-of-band). Guard against a concurrent insert.
    session.execute(
        insert(Symbol)
        .values(slug=slug, names={}, lens_meanings={})
        .on_conflict_do_nothing(index_elements=[Symbol.slug])
    )
    session.flush()
    symbol_id = session.scalar(select(Symbol.id).where(Symbol.slug == slug))
    assert symbol_id is not None
    return symbol_id


def _persist_emotions(session: Session, dream_id: uuid.UUID, extraction: DreamExtraction) -> None:
    for item in extraction.emotions:
        emotion_id = _get_or_create_emotion(session, item.slug)
        session.execute(
            insert(DreamEmotion)
            .values(dream_id=dream_id, emotion_id=emotion_id, kind=item.kind)
            .on_conflict_do_nothing(
                index_elements=[
                    DreamEmotion.dream_id,
                    DreamEmotion.emotion_id,
                    DreamEmotion.kind,
                ]
            )
        )
    session.flush()


def _get_or_create_emotion(session: Session, slug: str) -> int:
    existing = session.scalar(select(Emotion.id).where(Emotion.slug == slug))
    if existing is not None:
        return existing
    session.execute(
        insert(Emotion).values(slug=slug).on_conflict_do_nothing(index_elements=[Emotion.slug])
    )
    session.flush()
    emotion_id = session.scalar(select(Emotion.id).where(Emotion.slug == slug))
    assert emotion_id is not None
    return emotion_id


def _persist_embedding(session: Session, dream_id: uuid.UUID, transcript: str) -> None:
    vector = embeddings.embed(transcript)
    session.execute(
        insert(DreamEmbedding)
        .values(dream_id=dream_id, embedding=vector)
        .on_conflict_do_update(index_elements=[DreamEmbedding.dream_id], set_={"embedding": vector})
    )
    session.flush()


def _lens_meanings(
    session: Session, slug_to_id: dict[str, uuid.UUID], lens: Lens
) -> dict[str, str]:
    """Base meanings for the chosen lens, for symbols that have them seeded."""
    meanings: dict[str, str] = {}
    if not slug_to_id:
        return meanings
    rows = session.execute(
        select(Symbol.slug, Symbol.lens_meanings).where(Symbol.slug.in_(slug_to_id.keys()))
    ).all()
    for slug, lens_meanings in rows:
        value = (lens_meanings or {}).get(lens.value)
        if value:
            meanings[slug] = value
    return meanings


def _symbols_line(extraction: DreamExtraction) -> str:
    return ", ".join(f"{s.slug}: {s.salience:.2f}" for s in extraction.symbols)


def _emotions_line(extraction: DreamExtraction) -> str:
    return ", ".join(f"{e.slug} ({e.kind})" for e in extraction.emotions)


def _meanings_block(meanings: dict[str, str]) -> str:
    return "\n".join(f"- {slug}: {text}" for slug, text in meanings.items())
