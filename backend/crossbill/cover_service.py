"""Service for fetching and managing book cover images."""

import logging
from http import HTTPStatus
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# OpenLibrary covers API
OPENLIBRARY_COVER_URL = "https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

# Directory to store book covers
COVERS_DIR = Path(__file__).parent.parent / "book-covers"


def fetch_book_cover(isbn: str, book_id: int) -> str | None:
    """
    Fetch book cover from OpenLibrary API and save it locally.

    Args:
        isbn: Book ISBN number
        book_id: Database ID of the book (used for filename)

    Returns:
        str | None: Relative path to saved cover image, or None if fetch failed
    """
    if not isbn:
        logger.debug("No ISBN provided, skipping cover fetch")
        return None

    # Ensure covers directory exists
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename using book ID
    cover_filename = f"{book_id}.jpg"
    cover_path = COVERS_DIR / cover_filename

    # If cover already exists, return the path
    if cover_path.exists():
        logger.debug(f"Cover already exists for book {book_id}")
        return f"/media/covers/{cover_filename}"

    # Download and save the cover
    result = _download_cover(isbn, book_id, cover_path)
    if result:
        return f"/media/covers/{cover_filename}"
    return None


def _download_cover(isbn: str, book_id: int, cover_path: Path) -> bool:
    """Download cover image from OpenLibrary and save to disk."""
    try:
        url = OPENLIBRARY_COVER_URL.format(isbn=isbn)
        logger.info(f"Fetching cover from OpenLibrary for ISBN {isbn}: {url}")

        response = httpx.get(url, timeout=10.0, follow_redirects=True)

        # OpenLibrary returns 404 with a default "cover not found" image
        if response.status_code == HTTPStatus.NOT_FOUND:
            logger.info(f"No cover found on OpenLibrary for ISBN {isbn}")
            return False

        if response.status_code != HTTPStatus.OK:
            logger.warning(f"Failed to fetch cover for ISBN {isbn}: HTTP {response.status_code}")
            return False

        # Check if we got an actual image
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            logger.warning(f"Unexpected content type for ISBN {isbn}: {content_type}")
            return False

        # Save the image
        cover_path.write_bytes(response.content)
        logger.info(f"Successfully saved cover for book {book_id} at {cover_path}")
        return True

    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching cover for ISBN {isbn}")
    except httpx.RequestError as e:
        logger.warning(f"Request error fetching cover for ISBN {isbn}: {e}")
    except OSError as e:
        logger.error(f"Failed to save cover image for book {book_id}: {e}")

    return False
