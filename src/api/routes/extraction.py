"""Extraction API endpoints with file upload support."""

import logging
import os
import tempfile
from typing import Optional

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from src.dependencies import CurrentUser
from src.services.extraction_service import ExtractionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post("/extract")
async def extract_data(user: CurrentUser, file: UploadFile = File(...)):
    """Extract data from uploaded document.

    Supports:
    - Plain text files (.txt)
    - PDF files (.pdf)
    - DOCX files (.docx)

    For images and advanced OCR, AWS Textract integration would be needed.
    """
    try:
        # Validate file type
        allowed_types = [
            "text/plain",
            "text/csv",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        # Check if file type is allowed or if it's a CSV file (which may come as application/octet-stream)
        is_allowed = file.content_type in allowed_types
        is_csv_file = (
            file.content_type == "application/octet-stream"
            and file.filename
            and file.filename.lower().endswith(".csv")
        )

        if not (is_allowed or is_csv_file):
            supported_types = allowed_types + ["text/csv (detected by filename)"]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Supported: {', '.join(supported_types)}",
            )

        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File too large. Maximum size: 10MB"
            )

        # Save file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename or "file")[1]
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Extract text
            extraction_service = ExtractionService()
            result = await extraction_service.extract_text(temp_file_path)

            return JSONResponse(status_code=status.HTTP_200_OK, content=result)

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file_path}: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text extraction failed: {str(e)}",
        )
