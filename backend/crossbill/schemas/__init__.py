"""Pydantic schemas for API request/response validation."""

from crossbill.schemas.book_schemas import (
    Book,
    BookBase,
    BookCreate,
    BooksListResponse,
    BookWithHighlightCount,
    CoverUploadResponse,
)
from crossbill.schemas.chapter_schemas import Chapter, ChapterBase
from crossbill.schemas.highlight_schemas import (
    BookDetails,
    ChapterWithHighlights,
    Highlight,
    HighlightBase,
    HighlightCreate,
    HighlightDeleteRequest,
    HighlightDeleteResponse,
    HighlightSearchResponse,
    HighlightSearchResult,
    HighlightUploadRequest,
    HighlightUploadResponse,
)

__all__ = [
    # Book schemas
    "Book",
    "BookBase",
    "BookCreate",
    "BookWithHighlightCount",
    "BooksListResponse",
    "BookDetails",
    "CoverUploadResponse",
    # Chapter schemas
    "Chapter",
    "ChapterBase",
    "ChapterWithHighlights",
    # Highlight schemas
    "Highlight",
    "HighlightBase",
    "HighlightCreate",
    "HighlightUploadRequest",
    "HighlightUploadResponse",
    "HighlightDeleteRequest",
    "HighlightDeleteResponse",
    "HighlightSearchResult",
    "HighlightSearchResponse",
]
