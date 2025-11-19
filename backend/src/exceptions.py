"""Custom exception hierarchy for Crossbill application."""


class CrossbillError(Exception):
    """Base exception for all Crossbill errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        """Initialize exception with message and optional status code."""
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(CrossbillError):
    """Resource not found error."""


class BookNotFoundError(NotFoundError):
    """Book not found error."""

    def __init__(self, book_id: int) -> None:
        """Initialize with book ID."""
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} not found")


class ValidationError(CrossbillError):
    """Validation error."""


class ServiceError(CrossbillError):
    """Service layer error."""
