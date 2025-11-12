"""Repository layer for database operations using repository pattern."""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crossbill import models, schemas

logger = logging.getLogger(__name__)


class BookRepository:
    """Repository for Book database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def find_by_title_and_author(self, title: str, author: str | None) -> models.Book | None:
        """Find a book by its title and author."""
        stmt = select(models.Book).where(models.Book.title == title, models.Book.author == author)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, book_data: schemas.BookCreate) -> models.Book:
        """Create a new book."""
        book = models.Book(**book_data.model_dump())
        self.db.add(book)
        self.db.flush()
        self.db.refresh(book)
        logger.info(f"Created book: {book.title} (id={book.id})")
        return book

    def update(self, book: models.Book, book_data: schemas.BookCreate) -> models.Book:
        """Update an existing book's metadata."""
        book.title = book_data.title
        book.author = book_data.author
        book.isbn = book_data.isbn
        self.db.flush()
        self.db.refresh(book)
        logger.info(f"Updated book: {book.title} (id={book.id})")
        return book

    def get_or_create(self, book_data: schemas.BookCreate) -> models.Book:
        """Get existing book by title and author or create a new one."""
        book = self.find_by_title_and_author(book_data.title, book_data.author)

        if book:
            # Update metadata in case it changed
            return self.update(book, book_data)

        # Create new book
        return self.create(book_data)

    def get_books_with_highlight_count(
        self, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[tuple[models.Book, int]], int]:
        """
        Get books with their highlight counts, sorted alphabetically by title.

        Args:
            offset: Number of books to skip (default: 0)
            limit: Maximum number of books to return (default: 100)

        Returns:
            tuple[Sequence[tuple[Book, int]], int]: (list of (book, count) tuples, total count)
        """
        # Count query for total number of books
        total_stmt = select(func.count(models.Book.id))
        total = self.db.execute(total_stmt).scalar() or 0

        # Main query for books with highlight counts (excluding soft-deleted highlights)
        stmt = (
            select(models.Book, func.count(models.Highlight.id).label("highlight_count"))
            .outerjoin(
                models.Highlight,
                (models.Book.id == models.Highlight.book_id)
                & (models.Highlight.deleted_at.is_(None)),
            )
            .group_by(models.Book.id)
            .order_by(models.Book.title)
            .offset(offset)
            .limit(limit)
        )

        result = self.db.execute(stmt).all()
        return result, total

    def get_by_id(self, book_id: int) -> models.Book | None:
        """Get a book by its ID."""
        stmt = select(models.Book).where(models.Book.id == book_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def delete(self, book_id: int) -> bool:
        """
        Delete a book by its ID (hard delete).

        Args:
            book_id: ID of the book to delete

        Returns:
            bool: True if book was deleted, False if book was not found
        """
        book = self.get_by_id(book_id)
        if not book:
            return False

        self.db.delete(book)
        self.db.flush()
        logger.info(f"Deleted book: {book.title} (id={book.id})")
        return True


class ChapterRepository:
    """Repository for Chapter database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def find_by_name_and_book(self, book_id: int, name: str) -> models.Chapter | None:
        """Find a chapter by name and book ID."""
        stmt = select(models.Chapter).where(
            models.Chapter.book_id == book_id, models.Chapter.name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self, book_id: int, name: str, chapter_number: int | None = None
    ) -> models.Chapter:
        """Create a new chapter."""
        chapter = models.Chapter(book_id=book_id, name=name, chapter_number=chapter_number)
        self.db.add(chapter)
        self.db.flush()
        self.db.refresh(chapter)
        logger.info(f"Created chapter: {name} for book_id={book_id} (number={chapter_number})")
        return chapter

    def update_chapter_number(self, chapter_id: int, chapter_number: int | None) -> models.Chapter:
        """Update the chapter number for an existing chapter."""
        stmt = select(models.Chapter).where(models.Chapter.id == chapter_id)
        chapter = self.db.execute(stmt).scalar_one_or_none()
        if chapter:
            chapter.chapter_number = chapter_number
            self.db.flush()
            self.db.refresh(chapter)
            logger.info(f"Updated chapter {chapter_id} number to {chapter_number}")
        return chapter

    def get_or_create(
        self, book_id: int, name: str, chapter_number: int | None = None
    ) -> models.Chapter:
        """Get existing chapter by name and book or create a new one."""
        chapter = self.find_by_name_and_book(book_id, name)

        if chapter:
            # Update chapter number if it's different
            if chapter_number is not None and chapter.chapter_number != chapter_number:
                chapter.chapter_number = chapter_number
                self.db.flush()
                self.db.refresh(chapter)
                logger.info(
                    f"Updated chapter number for '{name}' (book_id={book_id}) to {chapter_number}"
                )
            return chapter

        try:
            return self.create(book_id, name, chapter_number)
        except IntegrityError:
            # Handle race condition: another request created the chapter
            self.db.rollback()
            chapter = self.find_by_name_and_book(book_id, name)
            if chapter:
                # Update chapter number if it's different
                if chapter_number is not None and chapter.chapter_number != chapter_number:
                    chapter.chapter_number = chapter_number
                    self.db.flush()
                    self.db.refresh(chapter)
                return chapter
            raise

    def get_by_book_id(self, book_id: int) -> Sequence[models.Chapter]:
        """Get all chapters for a book, ordered by chapter_number if available."""
        stmt = (
            select(models.Chapter)
            .where(models.Chapter.book_id == book_id)
            .order_by(
                # Order by chapter_number if available, otherwise by name
                # NULL chapter_numbers go to the end
                models.Chapter.chapter_number.is_(None),
                models.Chapter.chapter_number,
                models.Chapter.name,
            )
        )
        return self.db.execute(stmt).scalars().all()


class HighlightRepository:
    """Repository for Highlight database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(self, book_id: int, highlight_data: schemas.HighlightCreate) -> models.Highlight:
        """Create a new highlight."""
        highlight = models.Highlight(
            book_id=book_id, **highlight_data.model_dump(exclude={"chapter", "chapter_number"})
        )
        self.db.add(highlight)
        self.db.flush()
        self.db.refresh(highlight)
        return highlight

    def create_with_chapter(
        self, book_id: int, chapter_id: int | None, highlight_data: schemas.HighlightCreate
    ) -> models.Highlight:
        """Create a new highlight with chapter association."""
        highlight = models.Highlight(
            book_id=book_id,
            chapter_id=chapter_id,
            **highlight_data.model_dump(exclude={"chapter", "chapter_number"}),
        )
        self.db.add(highlight)
        self.db.flush()
        self.db.refresh(highlight)
        return highlight

    def try_create(
        self, book_id: int, chapter_id: int | None, highlight_data: schemas.HighlightCreate
    ) -> tuple[models.Highlight | None, bool]:
        """
        Try to create a highlight.

        Returns:
            tuple[Highlight | None, bool]: (highlight, was_created)
            If duplicate (including soft-deleted), returns (None, False)
        """
        try:
            highlight = self.create_with_chapter(book_id, chapter_id, highlight_data)
            return highlight, True
        except IntegrityError:
            # Duplicate - unique constraint violated (active or soft-deleted)
            self.db.rollback()
            logger.debug(
                f"Skipped duplicate highlight for book_id={book_id}, "
                f"text='{highlight_data.text[:50]}...'"
            )
            return None, False

    def bulk_create(
        self, book_id: int, highlights_data: list[tuple[int | None, schemas.HighlightCreate]]
    ) -> tuple[int, int]:
        """
        Bulk create highlights with deduplication.

        Args:
            book_id: ID of the book
            highlights_data: List of (chapter_id, highlight_data) tuples

        Returns:
            tuple[int, int]: (created_count, skipped_count)
        """
        created = 0
        skipped = 0

        for chapter_id, highlight_data in highlights_data:
            _, was_created = self.try_create(book_id, chapter_id, highlight_data)
            if was_created:
                created += 1
            else:
                skipped += 1

        logger.info(
            f"Bulk created highlights for book_id={book_id}: "
            f"{created} created, {skipped} skipped"
        )
        return created, skipped

    def find_by_book(self, book_id: int) -> Sequence[models.Highlight]:
        """Find all non-deleted highlights for a book."""
        stmt = select(models.Highlight).where(
            models.Highlight.book_id == book_id, models.Highlight.deleted_at.is_(None)
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_chapter(self, chapter_id: int) -> Sequence[models.Highlight]:
        """Find all non-deleted highlights for a chapter, ordered by datetime."""
        stmt = (
            select(models.Highlight)
            .where(models.Highlight.chapter_id == chapter_id, models.Highlight.deleted_at.is_(None))
            .order_by(models.Highlight.datetime)
        )
        return self.db.execute(stmt).scalars().all()

    def search(
        self, search_text: str, book_id: int | None = None, limit: int = 100
    ) -> Sequence[models.Highlight]:
        """
        Search for highlights using full-text search (PostgreSQL) or LIKE (SQLite).

        Args:
            search_text: Text to search for
            book_id: Optional book ID to filter by
            limit: Maximum number of results to return (default 100)

        Returns:
            Sequence of matching highlights with their relationships loaded
        """
        # Check database type
        is_postgresql = self.db.bind.dialect.name == "postgresql"

        # Build the base query with eager loading of relationships
        stmt = (
            select(models.Highlight)
            .join(models.Book)
            .outerjoin(models.Chapter, models.Highlight.chapter_id == models.Chapter.id)
            .where(models.Highlight.deleted_at.is_(None))
        )

        if is_postgresql:
            # PostgreSQL: Use full-text search
            search_query = func.plainto_tsquery("english", search_text)
            stmt = stmt.where(models.Highlight.text_search_vector.op("@@")(search_query))
        else:
            # SQLite: Use LIKE-based search
            stmt = stmt.where(models.Highlight.text.ilike(f"%{search_text}%"))

        # Add optional book_id filter
        if book_id is not None:
            stmt = stmt.where(models.Highlight.book_id == book_id)

        # Order by relevance and limit results
        if is_postgresql:
            search_query = func.plainto_tsquery("english", search_text)
            stmt = stmt.order_by(
                func.ts_rank(models.Highlight.text_search_vector, search_query).desc()
            )
        else:
            # SQLite: Order by created_at (newest first)
            stmt = stmt.order_by(models.Highlight.created_at.desc())

        stmt = stmt.limit(limit)

        return self.db.execute(stmt).scalars().all()

    def soft_delete_by_ids(self, book_id: int, highlight_ids: list[int]) -> int:
        """
        Soft delete highlights by their IDs for a specific book.

        Args:
            book_id: ID of the book (for validation)
            highlight_ids: List of highlight IDs to soft delete

        Returns:
            int: Number of highlights soft deleted
        """
        # Find highlights that belong to the book and are not already deleted
        stmt = select(models.Highlight).where(
            models.Highlight.id.in_(highlight_ids),
            models.Highlight.book_id == book_id,
            models.Highlight.deleted_at.is_(None),
        )
        highlights = self.db.execute(stmt).scalars().all()

        # Soft delete each highlight
        count = 0
        for highlight in highlights:
            highlight.deleted_at = datetime.now(UTC)
            count += 1

        self.db.flush()
        logger.info(f"Soft deleted {count} highlights for book_id={book_id}")
        return count
