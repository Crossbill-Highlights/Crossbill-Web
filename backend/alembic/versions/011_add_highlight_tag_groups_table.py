"""Add highlight_tag_groups table and tag_group_id to highlight_tags.

Revision ID: 011
Revises: 010
Create Date: 2025-11-18 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011"
down_revision: str | None = "010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create highlight_tag_groups table and add tag_group_id to highlight_tags."""
    # Create highlight_tag_groups table
    op.create_table(
        "highlight_tag_groups",
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
        sa.UniqueConstraint("book_id", "name", name="uq_highlight_tag_group_book_name"),
    )
    op.create_index(
        op.f("ix_highlight_tag_groups_id"), "highlight_tag_groups", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_highlight_tag_groups_book_id"), "highlight_tag_groups", ["book_id"], unique=False
    )
    op.create_index(
        op.f("ix_highlight_tag_groups_name"), "highlight_tag_groups", ["name"], unique=False
    )

    # Add tag_group_id column to highlight_tags
    op.add_column(
        "highlight_tags",
        sa.Column("tag_group_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_highlight_tags_tag_group_id",
        "highlight_tags",
        "highlight_tag_groups",
        ["tag_group_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_highlight_tags_tag_group_id"), "highlight_tags", ["tag_group_id"], unique=False
    )


def downgrade() -> None:
    """Drop tag_group_id from highlight_tags and drop highlight_tag_groups table."""
    # Drop tag_group_id column from highlight_tags
    op.drop_index(op.f("ix_highlight_tags_tag_group_id"), table_name="highlight_tags")
    op.drop_constraint("fk_highlight_tags_tag_group_id", "highlight_tags", type_="foreignkey")
    op.drop_column("highlight_tags", "tag_group_id")

    # Drop highlight_tag_groups table
    op.drop_index(op.f("ix_highlight_tag_groups_name"), table_name="highlight_tag_groups")
    op.drop_index(op.f("ix_highlight_tag_groups_book_id"), table_name="highlight_tag_groups")
    op.drop_index(op.f("ix_highlight_tag_groups_id"), table_name="highlight_tag_groups")
    op.drop_table("highlight_tag_groups")
