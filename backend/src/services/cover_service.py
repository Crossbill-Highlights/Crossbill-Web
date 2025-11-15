"""Service for fetching and managing book cover images."""

import logging
from http import HTTPStatus
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from src import models

logger = logging.getLogger(__name__)

# OpenLibrary covers API
OPENLIBRARY_COVER_URL = "https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

# Directory to store book covers
COVERS_DIR = Path(__file__).parent.parent.parent / "book-covers"


async def fetch_and_save_book_cover(isbn: str, book_id: int, db: Session) -> None:
    """
    Fetch book cover from OpenLibrary API, save it locally, and update database.

    This function is designed to be called as a background task and will not
    block the HTTP response. It fetches the cover asynchronously and updates
    the book record in the database.

    Args:
        isbn: Book ISBN number
        book_id: Database ID of the book
        db: Database session for updating the book record
    """
    if not isbn:
        logger.debug("No ISBN provided, skipping cover fetch")
        return

    # Ensure covers directory exists
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename using book ID
    cover_filename = f"{book_id}.jpg"
    cover_path = COVERS_DIR / cover_filename

    # If cover already exists, skip fetch but update database if needed
    if cover_path.exists():
        logger.debug(f"Cover already exists for book {book_id}")
        cover_url = f"/media/covers/{cover_filename}"
        _update_book_cover(book_id, cover_url, db)
        return

    # Download and save the cover
    cover_url = await _download_cover_async(isbn, book_id, cover_path)
    if cover_url:
        _update_book_cover(book_id, cover_url, db)


async def _download_cover_async(isbn: str, book_id: int, cover_path: Path) -> str | None:
    """Download cover image from OpenLibrary asynchronously and save to disk."""
    try:
        url = OPENLIBRARY_COVER_URL.format(isbn=isbn)
        logger.info(f"Fetching cover from OpenLibrary for ISBN {isbn}: {url}")

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0, follow_redirects=True)

            # OpenLibrary returns 404 with a default "cover not found" image
            if response.status_code == HTTPStatus.NOT_FOUND:
                logger.info(f"No cover found on OpenLibrary for ISBN {isbn}")
                return None

            if response.status_code != HTTPStatus.OK:
                logger.warning(
                    f"Failed to fetch cover for ISBN {isbn}: HTTP {response.status_code}"
                )
                return None

            # Check if we got an actual image
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                logger.warning(f"Unexpected content type for ISBN {isbn}: {content_type}")
                return None

            # Save the image
            cover_path.write_bytes(response.content)
            logger.info(f"Successfully saved cover for book {book_id} at {cover_path}")

            return f"/media/covers/{cover_path.name}"

    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching cover for ISBN {isbn}")
    except httpx.RequestError as e:
        logger.warning(f"Request error fetching cover for ISBN {isbn}: {e}")
    except OSError as e:
        logger.error(f"Failed to save cover image for book {book_id}: {e}")

    return None


def _update_book_cover(book_id: int, cover_url: str, db: Session) -> None:
    """Update the book's cover field in the database."""
    try:
        # Get the book
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if book and not book.cover:
            book.cover = cover_url
            db.commit()
            logger.info(f"Updated cover for book {book_id}: {cover_url}")
    except Exception as e:
        logger.error(f"Failed to update book cover in database for book {book_id}: {e}")
        db.rollback()
