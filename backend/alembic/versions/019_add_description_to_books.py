"""Add description column to books for storing book descriptions.

This migration adds a nullable description text column to the books table.
The description is extracted from KOReader ebook metadata during upload.

Revision ID: 019
Revises: 018
Create Date: 2025-12-24

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "019"
down_revision: str | None = "018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add description column to books table."""
    op.add_column(
        "books",
        sa.Column("description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Remove description column from books table."""
    op.drop_column("books", "description")
