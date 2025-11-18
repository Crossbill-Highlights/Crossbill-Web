"""
Crossbill API Client

Handles communication with the Crossbill backend server.
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from models import BooksListResponse, BookDetails, BookWithHighlightCount, Book, ChapterWithHighlights, Chapter, Highlight, HighlightTag


class CrossbillAPIError(Exception):
    """Raised when API request fails"""
    pass


class CrossbillAPI:
    """Client for communicating with Crossbill backend"""

    def __init__(self, server_host: str):
        """
        Initialize API client

        Args:
            server_host: Base URL of Crossbill server (e.g., 'http://localhost:8000')
        """
        self.server_host = server_host.rstrip('/')

    def _make_request(self, endpoint: str) -> dict:
        """
        Make HTTP GET request to API endpoint

        Args:
            endpoint: API endpoint path (e.g., '/api/v1/highlights/books')

        Returns:
            Parsed JSON response

        Raises:
            CrossbillAPIError: If request fails
        """
        url = f"{self.server_host}{endpoint}"

        try:
            request = urllib.request.Request(url)
            request.add_header('Accept', 'application/json')

            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code}: {e.reason}"
            try:
                error_body = e.read().decode('utf-8')
                error_data = json.loads(error_body)
                if 'detail' in error_data:
                    error_msg += f" - {error_data['detail']}"
            except:
                pass
            raise CrossbillAPIError(f"Failed to fetch {endpoint}: {error_msg}") from e

        except urllib.error.URLError as e:
            raise CrossbillAPIError(f"Network error: {e.reason}") from e

        except json.JSONDecodeError as e:
            raise CrossbillAPIError(f"Invalid JSON response: {e}") from e

        except Exception as e:
            raise CrossbillAPIError(f"Unexpected error: {e}") from e

    def get_books(self, limit: int = 1000, offset: int = 0) -> BooksListResponse:
        """
        Fetch list of books with highlight counts

        Args:
            limit: Maximum number of books to fetch
            offset: Number of books to skip

        Returns:
            BooksListResponse containing list of books

        Raises:
            CrossbillAPIError: If request fails
        """
        endpoint = f"/api/v1/highlights/books?limit={limit}&offset={offset}"
        data = self._make_request(endpoint)

        books = []
        for book_data in data.get('books', []):
            book = BookWithHighlightCount(
                id=book_data['id'],
                title=book_data['title'],
                author=book_data.get('author'),
                isbn=book_data.get('isbn'),
                created_at=book_data['created_at'],
                updated_at=book_data['updated_at'],
                highlight_count=book_data['highlight_count']
            )
            books.append(book)

        return BooksListResponse(
            books=books,
            total=data.get('total', len(books)),
            offset=data.get('offset', 0),
            limit=data.get('limit', limit)
        )

    def get_book_details(self, book_id: int) -> BookDetails:
        """
        Fetch book details including all chapters and highlights

        Args:
            book_id: ID of the book to fetch

        Returns:
            BookDetails with chapters and highlights

        Raises:
            CrossbillAPIError: If request fails
        """
        endpoint = f"/api/v1/book/{book_id}"
        data = self._make_request(endpoint)

        # Parse chapters with highlights
        chapters = []
        for chapter_data in data.get('chapters', []):
            # Parse highlights for this chapter
            highlights = []
            for hl_data in chapter_data.get('highlights', []):
                # Parse tags
                tags = []
                for tag_data in hl_data.get('highlight_tags', []):
                    tags.append(HighlightTag(
                        id=tag_data['id'],
                        name=tag_data['name']
                    ))

                highlight = Highlight(
                    id=hl_data['id'],
                    book_id=hl_data['book_id'],
                    chapter_id=hl_data.get('chapter_id'),
                    text=hl_data['text'],
                    chapter=hl_data.get('chapter'),
                    page=hl_data.get('page'),
                    note=hl_data.get('note'),
                    datetime=hl_data['datetime'],
                    highlight_tags=tags,
                    created_at=hl_data['created_at'],
                    updated_at=hl_data['updated_at']
                )
                highlights.append(highlight)

            chapter = ChapterWithHighlights(
                id=chapter_data['id'],
                book_id=chapter_data['book_id'],
                name=chapter_data['name'],
                created_at=chapter_data['created_at'],
                updated_at=chapter_data['updated_at'],
                highlights=highlights
            )
            chapters.append(chapter)

        return BookDetails(
            id=data['id'],
            title=data['title'],
            author=data.get('author'),
            isbn=data.get('isbn'),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            chapters=chapters
        )

    def test_connection(self) -> bool:
        """
        Test if connection to Crossbill server is working

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.get_books(limit=1)
            return True
        except CrossbillAPIError:
            return False
