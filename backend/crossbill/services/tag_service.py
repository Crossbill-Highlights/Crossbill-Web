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

    def update_book_tags(
        self, book_id: int, tag_names: list[str], restore_soft_deleted: bool = True
    ) -> models.Book:
        """
        Update the tags associated with a book.

        This method will:
        - Create new tags if they don't exist
        - Replace the book's current tags with the provided tags
        - Reuse existing tags if they already exist
        - Handle soft deletion: tags not in the list are soft-deleted
        - Optionally restore soft-deleted tags if restore_soft_deleted is True

        Args:
            book_id: ID of the book to update
            tag_names: List of tag names to associate with the book
            restore_soft_deleted: If True, re-adding a previously soft-deleted tag will restore it.
                                 If False, soft-deleted tags remain deleted. Default is True.

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

        # Add new tags to book (or restore soft-deleted ones if restore_soft_deleted is True)
        for tag in tags:
            if restore_soft_deleted:
                # This will create new association or restore soft-deleted one
                self.tag_repo.add_tag_to_book(book_id, tag.id)
            else:
                # Only add if not soft-deleted
                # Check if the tag association exists and is soft-deleted
                from sqlalchemy import and_, select

                stmt = select(models.book_tags).where(
                    and_(
                        models.book_tags.c.book_id == book_id,
                        models.book_tags.c.tag_id == tag.id,
                    )
                )
                existing = self.db.execute(stmt).fetchone()

                # Only add if it doesn't exist or is not soft-deleted
                if not existing or existing.deleted_at is None:
                    self.tag_repo.add_tag_to_book(book_id, tag.id)

        # Soft delete tags not in the provided list
        self.tag_repo.remove_all_tags_from_book_except(book_id, tag_ids)

        self.db.flush()
        # Refresh book to get updated tags
        self.db.refresh(book)

        logger.info(f"Updated tags for book {book_id}: {[tag.name for tag in tags]}")
        return book

    def get_all_tags(self) -> list[models.Tag]:
        """Get all available tags."""
        return self.tag_repo.get_all()
