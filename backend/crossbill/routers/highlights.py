"""API routes for highlights management."""

import logging

from fastapi import APIRouter, HTTPException, status

from crossbill import schemas, services
from crossbill.database import DatabaseSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/highlights", tags=["highlights"])


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
