"""Custom exception hierarchy for Crossbill application."""


class CrossbillException(Exception):
    """Base exception for all Crossbill errors."""

    def __init__(self, message: str) -> None:
        """Initialize exception with message."""
        self.message = message
        super().__init__(self.message)


class NotFoundError(CrossbillException):
    """Resource not found error."""


class BookNotFoundError(NotFoundError):
    """Book not found error."""

    def __init__(self, book_id: int) -> None:
        """Initialize with book ID."""
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} not found")


class ValidationError(CrossbillException):
    """Validation error."""


class ServiceError(CrossbillException):
    """Service layer error."""
