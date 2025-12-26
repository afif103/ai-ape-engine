"""Extraction API endpoints with file upload support."""

import logging
import os
import tempfile
from typing import Optional

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from src.dependencies import CurrentUser
from src.services.extraction_service import ExtractionService
from src.services.processing_status import processing_tracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post("/extract")
async def extract_data(user: CurrentUser, file: UploadFile = File(...)):
    """Extract data from uploaded document with real-time processing status.

    Supports:
    - Plain text files (.txt) - AWS Comprehend analysis
    - CSV files (.csv) - Table detection + AWS Comprehend
    - PDF files (.pdf) - AWS Textract table/form detection
    - DOCX files (.docx) - AWS Textract table/form detection
    - Images (.png, .jpg) - AWS Textract OCR

    Returns job ID immediately, use /processing/status/{job_id} for real-time updates.
    """
    # Validate file type
    allowed_types = [
        "text/plain",
        "text/csv",
        "text/markdown",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]

    # Check if file type is allowed or if it's a CSV file (which may come as application/octet-stream)
    is_allowed = file.content_type in allowed_types
    is_csv_file = (
        file.content_type == "application/octet-stream" and
        file.filename and
        file.filename.lower().endswith('.csv')
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

    # Create processing job
    job_id = processing_tracker.create_job(
        file.filename or "uploaded_file",
        len(file_content)
    )

    # Start background processing
    import asyncio
    asyncio.create_task(process_file_background(temp_file_path, job_id))

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={
        "message": "File upload accepted, processing started",
        "job_id": job_id,
        "status_url": f"/api/v1/processing/status/{job_id}",
        "estimated_time": "10-30 seconds"
    })


async def process_file_background(file_path: str, job_id: str):
    """Process file in background and update job status."""
    try:
        extraction_service = ExtractionService()
        result = await extraction_service.extract_text(file_path, job_id)

        # Job completion is handled in the extraction service

    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")
        processing_tracker.fail_job(job_id, str(e))

    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {file_path}: {e}")

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

        # Create processing job
        job_id = processing_tracker.create_job(
            file.filename or "uploaded_file",
            len(file_content)
        )

        # Start background processing
        import asyncio
        asyncio.create_task(process_file_background(temp_file_path, job_id))

        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={
            "message": "File upload accepted, processing started",
            "job_id": job_id,
            "status_url": f"/api/v1/processing/status/{job_id}",
            "estimated_time": "10-30 seconds"
        })

    

async def process_file_background(file_path: str, job_id: str):
    """Process file in background and update job status."""
    try:
        extraction_service = ExtractionService()
        result = await extraction_service.extract_text(file_path, job_id)

        # Job completion is handled in the extraction service

    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")
        processing_tracker.fail_job(job_id, str(e))

    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {file_path}: {e}")

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

