"""Add highlight_tags table.

Revision ID: 009
Revises: 008
Create Date: 2025-11-14 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: str | None = "008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create highlight_tags table."""
    op.create_table(
        "highlight_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
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
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("book_id", "name", name="uq_highlight_tag_book_name"),
    )
    op.create_index(op.f("ix_highlight_tags_id"), "highlight_tags", ["id"], unique=False)
    op.create_index(op.f("ix_highlight_tags_book_id"), "highlight_tags", ["book_id"], unique=False)
    op.create_index(op.f("ix_highlight_tags_name"), "highlight_tags", ["name"], unique=False)


def downgrade() -> None:
    """Drop highlight_tags table."""
    op.drop_index(op.f("ix_highlight_tags_name"), table_name="highlight_tags")
    op.drop_index(op.f("ix_highlight_tags_book_id"), table_name="highlight_tags")
    op.drop_index(op.f("ix_highlight_tags_id"), table_name="highlight_tags")
    op.drop_table("highlight_tags")
