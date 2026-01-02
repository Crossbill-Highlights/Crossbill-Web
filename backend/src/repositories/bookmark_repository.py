"""Bookmark repository for database operations."""

import logging
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from src import models

logger = logging.getLogger(__name__)


class BookmarkValidationResult(NamedTuple):
    """Result of validating book and highlight for bookmark creation."""

    book_exists: bool
    highlight_exists: bool
    highlight_belongs_to_book: bool
    existing_bookmark: models.Bookmark | None


class BookmarkRepository:
    """Repository for Bookmark database operations.

    Note: Bookmarks don't have direct user_id. User ownership is verified
    through the book relationship.
    """

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def validate_and_get_existing_bookmark(
        self, book_id: int, highlight_id: int, user_id: int
    ) -> BookmarkValidationResult:
        """
        Validate book and highlight for bookmark creation and check if bookmark already exists.

        This method performs all validation in a single query using JOINs:
        - Checks if book exists and belongs to user
        - Checks if highlight exists and belongs to user
        - Checks if highlight belongs to the book
        - Checks if bookmark already exists

        Args:
            book_id: ID of the book
            highlight_id: ID of the highlight
            user_id: ID of the user

        Returns:
            BookmarkValidationResult with validation status and existing bookmark if found
        """
        # Single query with LEFT JOINs to validate everything and check for existing bookmark
        stmt = (
            select(
                models.Book.id.label("book_id"),
                models.Highlight.id.label("highlight_id"),
                models.Highlight.book_id.label("highlight_book_id"),
                models.Bookmark,
            )
            .select_from(models.Book)
            .outerjoin(
                models.Highlight,
                (models.Highlight.id == highlight_id) & (models.Highlight.user_id == user_id),
            )
            .outerjoin(
                models.Bookmark,
                (models.Bookmark.book_id == book_id)
                & (models.Bookmark.highlight_id == highlight_id),
            )
            .where(models.Book.id == book_id, models.Book.user_id == user_id)
        )

        result = self.db.execute(stmt).one_or_none()

        # If no result, book doesn't exist
        if result is None:
            return BookmarkValidationResult(
                book_exists=False,
                highlight_exists=False,
                highlight_belongs_to_book=False,
                existing_bookmark=None,
            )

        book_id_result, highlight_id_result, highlight_book_id, existing_bookmark = result

        # Check validation conditions
        book_exists = book_id_result is not None
        highlight_exists = highlight_id_result is not None
        highlight_belongs_to_book = highlight_exists and highlight_book_id == book_id

        return BookmarkValidationResult(
            book_exists=book_exists,
            highlight_exists=highlight_exists,
            highlight_belongs_to_book=highlight_belongs_to_book,
            existing_bookmark=existing_bookmark,
        )

    def get_by_id(self, bookmark_id: int, user_id: int) -> models.Bookmark | None:
        """Get a bookmark by its ID, verifying user ownership through book."""
        stmt = (
            select(models.Bookmark)
            .join(models.Book, models.Bookmark.book_id == models.Book.id)
            .where(
                models.Bookmark.id == bookmark_id,
                models.Book.user_id == user_id,
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_book_id(self, book_id: int, user_id: int) -> list[models.Bookmark]:
        """Get all bookmarks for a specific book, verifying user ownership."""
        stmt = (
            select(models.Bookmark)
            .join(models.Book, models.Bookmark.book_id == models.Book.id)
            .where(
                models.Bookmark.book_id == book_id,
                models.Book.user_id == user_id,
            )
            .order_by(models.Bookmark.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(self, book_id: int, highlight_id: int, user_id: int) -> models.Bookmark:
        """Create a new bookmark.

        Note: Assumes book/highlight ownership has been verified by the caller.
        The user_id parameter is for logging purposes and future verification.
        """
        bookmark = models.Bookmark(book_id=book_id, highlight_id=highlight_id)
        self.db.add(bookmark)
        self.db.flush()
        self.db.refresh(bookmark)
        logger.info(
            f"Created bookmark: book_id={bookmark.book_id}, "
            f"highlight_id={bookmark.highlight_id} (id={bookmark.id}, user_id={user_id})"
        )
        return bookmark

    def delete(self, bookmark_id: int, user_id: int) -> bool:
        """Delete a bookmark by its ID, verifying user ownership.

        Returns True if deleted, False if not found or not owned by user.
        """
        bookmark = self.get_by_id(bookmark_id, user_id)
        if not bookmark:
            return False
        self.db.delete(bookmark)
        self.db.flush()
        logger.info(f"Deleted bookmark: id={bookmark_id}")
        return True
