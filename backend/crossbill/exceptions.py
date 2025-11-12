"""Custom exception hierarchy for Crossbill application."""


class CrossbillError(Exception):
    """Base exception for all Crossbill errors."""

    def __init__(self, message: str) -> None:
        """Initialize exception with message."""
        self.message = message
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
