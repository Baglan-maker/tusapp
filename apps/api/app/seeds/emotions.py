"""Seed the emotions reference table.

Idempotent: upserts by ``slug``.

    uv run python -m app.seeds.emotions
"""

from sqlalchemy.dialects.postgresql import insert

from app.db import SessionLocal
from app.models.emotion import Emotion

EMOTIONS: list[str] = [
    "fear",
    "joy",
    "anxiety",
    "sadness",
    "anger",
    "peace",
    "confusion",
    "excitement",
    "shame",
    "love",
    "surprise",
    "disgust",
]


def seed() -> int:
    """Upsert all emotions by slug. Returns the number of rows processed."""
    with SessionLocal() as session:
        for slug in EMOTIONS:
            stmt = insert(Emotion).values(slug=slug)
            stmt = stmt.on_conflict_do_nothing(index_elements=[Emotion.slug])
            session.execute(stmt)
        session.commit()
    return len(EMOTIONS)


if __name__ == "__main__":
    count = seed()
    print(f"Seeded {count} emotions.")
