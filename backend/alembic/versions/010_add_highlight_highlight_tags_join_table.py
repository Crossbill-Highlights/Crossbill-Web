"""Add highlight_highlight_tags join table for many-to-many relationship.

Revision ID: 010
Revises: 009
Create Date: 2025-11-14 00:01:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: str | None = "009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create highlight_highlight_tags join table."""
    op.create_table(
        "highlight_highlight_tags",
        sa.Column("highlight_id", sa.Integer(), nullable=False),
        sa.Column("highlight_tag_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["highlight_id"],
            ["highlights.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["highlight_tag_id"],
            ["highlight_tags.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("highlight_id", "highlight_tag_id"),
    )
    op.create_index(op.f("ix_highlight_highlight_tags_highlight_id"), "highlight_highlight_tags", ["highlight_id"], unique=False)
    op.create_index(op.f("ix_highlight_highlight_tags_highlight_tag_id"), "highlight_highlight_tags", ["highlight_tag_id"], unique=False)


def downgrade() -> None:
    """Drop highlight_highlight_tags join table."""
    op.drop_index(op.f("ix_highlight_highlight_tags_highlight_tag_id"), table_name="highlight_highlight_tags")
    op.drop_index(op.f("ix_highlight_highlight_tags_highlight_id"), table_name="highlight_highlight_tags")
    op.drop_table("highlight_highlight_tags")
