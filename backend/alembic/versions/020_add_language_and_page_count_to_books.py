"""Add language and page_count columns to books for storing book metadata.

This migration adds:
- language: Language code from ebook metadata (e.g., 'en', 'de')
- page_count: Total page count from ebook metadata

Both columns are nullable as they may not be available for all ebooks.

Revision ID: 020
Revises: 019
Create Date: 2025-12-24

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "020"
down_revision: str | None = "019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add language and page_count columns to books table."""
    op.add_column(
        "books",
        sa.Column("language", sa.String(10), nullable=True),
    )
    op.add_column(
        "books",
        sa.Column("page_count", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Remove language and page_count columns from books table."""
    op.drop_column("books", "page_count")
    op.drop_column("books", "language")
