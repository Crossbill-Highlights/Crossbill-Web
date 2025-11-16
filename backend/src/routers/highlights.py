"""API routes for highlights management."""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from src import schemas
from src.database import DatabaseSession
from src.services import HighlightService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/highlights", tags=["highlights"])


@router.get("/books", response_model=schemas.BooksListResponse, status_code=status.HTTP_200_OK)
def get_books(
    db: DatabaseSession,
    offset: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of books to return"),
    search: str | None = Query(None, description="Search text to filter books by title or author"),
) -> schemas.BooksListResponse:
    """
    Get all books with their highlight counts, sorted alphabetically by title.

    Args:
        db: Database session
        offset: Number of books to skip (for pagination)
        limit: Maximum number of books to return (for pagination)
        search: Optional search text to filter books by title or author

    Returns:
        BooksListResponse with list of books and pagination info

    Raises:
        HTTPException: If fetching books fails due to server error
    """
    try:
        service = HighlightService(db)
        return service.get_books_with_counts(offset, limit, search)
    except Exception as e:
        logger.error(f"Failed to fetch books: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch books: {e!s}",
        ) from e


@router.post(
    "/upload", response_model=schemas.HighlightUploadResponse, status_code=status.HTTP_200_OK
)
async def upload_highlights(
    request: schemas.HighlightUploadRequest,
    background_tasks: BackgroundTasks,
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
        service = HighlightService(db)
        return service.upload_highlights(request, background_tasks)
    except Exception as e:
        logger.error(f"Failed to upload highlights: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {e!s}",
        ) from e


@router.get(
    "/search", response_model=schemas.HighlightSearchResponse, status_code=status.HTTP_200_OK
)
def search_highlights(
    db: DatabaseSession,
    search_text: str = Query(
        ..., alias="searchText", min_length=1, description="Text to search for in highlights"
    ),
    book_id: int | None = Query(
        None, alias="bookId", ge=1, description="Optional book ID to filter results"
    ),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results to return"),
) -> schemas.HighlightSearchResponse:
    """
    Search for highlights using full-text search.

    Searches across all highlight text using PostgreSQL full-text search.
    Results are ranked by relevance and excludes soft-deleted highlights.

    Args:
        db: Database session
        search_text: Text to search for
        book_id: Optional book ID to filter by specific book
        limit: Maximum number of results to return

    Returns:
        HighlightSearchResponse with matching highlights and their book/chapter data

    Raises:
        HTTPException: If search fails due to server error
    """
    try:
        service = HighlightService(db)
        return service.search_highlights(search_text, book_id, limit)
    except Exception as e:
        logger.error(f"Failed to search highlights: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {e!s}",
        ) from e
