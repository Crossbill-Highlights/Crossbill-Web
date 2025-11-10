"""Add full-text search support to highlights table.

Revision ID: 005
Revises: 004
Create Date: 2025-11-10 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add tsvector column and GIN index for full-text search."""
    # Check if we're using PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Add tsvector column for full-text search (PostgreSQL only)
        op.add_column(
            "highlights",
            sa.Column(
                "text_search_vector",
                postgresql.TSVECTOR,
                nullable=True,
            ),
        )

        # Create GIN index for fast full-text searches
        op.create_index(
            "ix_highlights_text_search_vector",
            "highlights",
            ["text_search_vector"],
            postgresql_using="gin",
        )

        # Populate the tsvector column with existing data
        op.execute(
            """
            UPDATE highlights
            SET text_search_vector = to_tsvector('english', COALESCE(text, ''))
            WHERE text_search_vector IS NULL
            """
        )

        # Create a trigger to automatically update the tsvector column
        op.execute(
            """
            CREATE FUNCTION highlights_text_search_vector_update() RETURNS trigger AS $$
            BEGIN
                NEW.text_search_vector := to_tsvector('english', COALESCE(NEW.text, ''));
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
            """
        )

        op.execute(
            """
            CREATE TRIGGER highlights_text_search_vector_trigger
            BEFORE INSERT OR UPDATE ON highlights
            FOR EACH ROW
            EXECUTE FUNCTION highlights_text_search_vector_update();
            """
        )


def downgrade() -> None:
    """Remove full-text search support."""
    # Check if we're using PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Drop trigger and function
        op.execute("DROP TRIGGER IF EXISTS highlights_text_search_vector_trigger ON highlights")
        op.execute("DROP FUNCTION IF EXISTS highlights_text_search_vector_update()")

        # Drop index and column
        op.drop_index("ix_highlights_text_search_vector", table_name="highlights")
        op.drop_column("highlights", "text_search_vector")
