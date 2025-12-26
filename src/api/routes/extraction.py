"""Extraction API endpoints (placeholder)."""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.dependencies import CurrentUser
from src.services.extraction_service import ExtractionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extraction", tags=["extraction"])


class ExtractionRequest(BaseModel):
    """Request for data extraction."""

    file_path: str  # In real implementation, would be file upload


@router.post("/extract")
async def extract_data(data: ExtractionRequest, user: CurrentUser):
    """Extract data from document (placeholder).

    Note: Full implementation requires:
    - File upload handling
    - AWS Textract configuration
    - Schema validation
    """
    try:
        extraction_service = ExtractionService()
        result = await extraction_service.extract_text(data.file_path)
        return result
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
