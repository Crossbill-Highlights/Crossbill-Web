"""Service layer for tag-related business logic."""

import logging

from sqlalchemy.orm import Session

from crossbill import models, repositories

logger = logging.getLogger(__name__)


class TagService:
    """Service for handling tag-related operations."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db
        self.tag_repo = repositories.TagRepository(db)
        self.book_repo = repositories.BookRepository(db)

    def update_book_tags(self, book_id: int, tag_names: list[str]) -> models.Book:
        """
        Update the tags associated with a book (typically from UI).

        This method is designed for user-initiated tag updates. It will:
        - Create new tags if they don't exist
        - Add new tags to the book
        - Restore soft-deleted tags if the user re-adds them
        - Soft delete tags not in the provided list

        Args:
            book_id: ID of the book to update
            tag_names: List of tag names to associate with the book

        Returns:
            Updated book with new tags

        Raises:
            ValueError: If book is not found
        """
        return self._apply_tags_to_book(book_id, tag_names, restore_soft_deleted=True)

    def sync_book_tags_from_source(self, book_id: int, tag_names: list[str]) -> models.Book:
        """
        Sync book tags from external source (e.g., KOReader upload).

        This method is designed for automated tag syncing from external sources.
        It respects user deletions by NOT restoring soft-deleted tags. It will:
        - Create new tags if they don't exist
        - Add new tags to the book (but skip soft-deleted ones)
        - Soft delete tags not in the provided list
        - NEVER restore tags that were previously soft-deleted

        Use this when syncing from KOReader or other external sources where
        we want to respect tags that users have explicitly removed.

        Args:
            book_id: ID of the book to update
            tag_names: List of tag names to associate with the book

        Returns:
            Updated book with new tags

        Raises:
            ValueError: If book is not found
        """
        return self._apply_tags_to_book(book_id, tag_names, restore_soft_deleted=False)

    def _apply_tags_to_book(
        self, book_id: int, tag_names: list[str], restore_soft_deleted: bool
    ) -> models.Book:
        """
        Internal helper to apply tags to a book with specified restore behavior.

        Args:
            book_id: ID of the book to update
            tag_names: List of tag names to associate with the book
            restore_soft_deleted: Whether to restore soft-deleted tag associations

        Returns:
            Updated book with new tags

        Raises:
            ValueError: If book is not found
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id {book_id} not found")

        # Get or create tags
        tags = []
        tag_ids = []
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:  # Skip empty strings
                tag = self.tag_repo.get_or_create(tag_name)
                tags.append(tag)
                tag_ids.append(tag.id)

        # Add tags to book based on restore policy
        for tag in tags:
            if restore_soft_deleted:
                # Always add/restore - used for UI updates
                self.tag_repo.add_tag_to_book(book_id, tag.id)
            else:
                # Skip soft-deleted tags - used for external source syncing
                if not self.tag_repo.is_tag_soft_deleted_for_book(book_id, tag.id):
                    self.tag_repo.add_tag_to_book(book_id, tag.id)

        # Soft delete tags not in the provided list
        self.tag_repo.remove_all_tags_from_book_except(book_id, tag_ids)

        self.db.flush()
        self.db.refresh(book)

        logger.info(f"Applied tags for book {book_id}: {[tag.name for tag in tags]}")
        return book

    def get_all_tags(self) -> list[models.Tag]:
        """Get all available tags."""
        return self.tag_repo.get_all()
