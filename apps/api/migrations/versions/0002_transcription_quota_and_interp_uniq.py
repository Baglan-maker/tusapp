"""transcription quota column + interpretation (dream, lens) uniqueness

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "usage_quota",
        sa.Column(
            "transcriptions_used",
            sa.SmallInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_interpretations_dream_lens", "interpretations", ["dream_id", "lens"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_interpretations_dream_lens", "interpretations", type_="unique")
    op.drop_column("usage_quota", "transcriptions_used")
