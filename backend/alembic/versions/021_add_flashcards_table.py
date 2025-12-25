"""Add flashcards table for study cards from highlights.

Revision ID: 021
Revises: 020
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "021"
down_revision: str | None = "020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create flashcards table."""
    op.create_table(
        "flashcards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("highlight_id", sa.Integer(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["highlight_id"], ["highlights.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_flashcards_id"), "flashcards", ["id"], unique=False)
    op.create_index(op.f("ix_flashcards_user_id"), "flashcards", ["user_id"], unique=False)
    op.create_index(op.f("ix_flashcards_book_id"), "flashcards", ["book_id"], unique=False)
    op.create_index(
        op.f("ix_flashcards_highlight_id"), "flashcards", ["highlight_id"], unique=False
    )


def downgrade() -> None:
    """Drop flashcards table."""
    op.drop_index(op.f("ix_flashcards_highlight_id"), table_name="flashcards")
    op.drop_index(op.f("ix_flashcards_book_id"), table_name="flashcards")
    op.drop_index(op.f("ix_flashcards_user_id"), table_name="flashcards")
    op.drop_index(op.f("ix_flashcards_id"), table_name="flashcards")
    op.drop_table("flashcards")
