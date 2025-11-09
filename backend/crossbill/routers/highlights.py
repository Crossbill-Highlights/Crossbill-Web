"""API routes for highlights management."""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from crossbill import repositories, schemas, services
from crossbill.database import DatabaseSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/highlights", tags=["highlights"])


@router.get("/books", response_model=schemas.BooksListResponse, status_code=status.HTTP_200_OK)
def get_books(
    db: DatabaseSession,
    offset: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of books to return"),
) -> schemas.BooksListResponse:
    """
    Get all books with their highlight counts, sorted alphabetically by title.

    Args:
        db: Database session
        offset: Number of books to skip (for pagination)
        limit: Maximum number of books to return (for pagination)

    Returns:
        BooksListResponse with list of books and pagination info

    Raises:
        HTTPException: If fetching books fails due to server error
    """
    try:
        book_repo = repositories.BookRepository(db)
        books_with_counts, total = book_repo.get_books_with_highlight_count(offset, limit)

        # Convert to response schema
        books_list = [
            schemas.BookWithHighlightCount(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                cover=book.cover,
                highlight_count=count,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            for book, count in books_with_counts
        ]

        return schemas.BooksListResponse(books=books_list, total=total, offset=offset, limit=limit)
    except Exception as e:
        logger.error(f"Failed to fetch books: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch books: {e!s}",
        ) from e


@router.post(
    "/upload", response_model=schemas.HighlightUploadResponse, status_code=status.HTTP_200_OK
)
def upload_highlights(
    request: schemas.HighlightUploadRequest,
    db: DatabaseSession,
) -> schemas.HighlightUploadResponse:
    """
    Upload highlights from KOReader.

    Creates or updates book record and adds highlights with automatic deduplication.
    Duplicates are identified by the combination of book, text, and datetime.

    Args:
        request: Highlight upload request containing book metadata and highlights
        db: Database session

    Returns:
        HighlightUploadResponse with upload statistics

    Raises:
        HTTPException: If upload fails due to server error
    """
    try:
        service = services.HighlightUploadService(db)
        return service.upload_highlights(request)
    except Exception as e:
        logger.error(f"Failed to upload highlights: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {e!s}",
        ) from e
