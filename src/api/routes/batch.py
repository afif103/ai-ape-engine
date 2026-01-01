"""Batch processing API routes."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse

from src.dependencies import CurrentUser, DatabaseSession
from src.models.user import User
from src.services.batch_processing_service import BatchProcessingService
from src.services.job_queue import job_queue

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/batch", tags=["batch"])


@router.post("/upload", response_model=dict)
async def create_batch_job(
    files: List[UploadFile] = File(...),
    batch_name: str = Form(..., description="Name for the batch job"),
    user: CurrentUser = None,
    db: DatabaseSession = None,
):
    """Create a batch job with multiple files for processing.

    Supports up to 10 files of mixed types:
    - CSV, TXT, PDF, DOCX, Images
    - Maximum 10MB per file
    """
    try:
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="At least one file is required"
            )

        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 10 files per batch"
            )

        # Validate files
        allowed_types = [
            "text/plain",
            "text/csv",
            "text/markdown",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/png",
            "image/jpeg",
            "image/jpg",
        ]

        file_metadata = []
        total_size = 0

        for file in files:
            # Read file content to validate
            content = await file.read()
            file_size = len(content)

            # Reset file pointer for potential reuse
            await file.seek(0)

            # Validate file type
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
                    detail=f"Unsupported file type for '{file.filename}': {file.content_type}. Supported: {', '.join(supported_types)}",
                )

            # Validate file size
            if file_size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{file.filename}' too large. Maximum size: 10MB",
                )

            total_size += file_size

            file_metadata.append(
                {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": file_size,
                    "temp_path": None,  # Will be set during processing
                }
            )

        # Create batch job
        batch_service = BatchProcessingService(db)
        batch_job = await batch_service.create_batch_job(
            user_id=user.id, batch_name=batch_name, files=file_metadata
        )

        # Enqueue for processing
        await job_queue.enqueue_batch_job(batch_job.id, priority=1)

        # Start background processing
        import asyncio

        asyncio.create_task(process_batch_background(batch_job.id))

        return {
            "message": f"Batch job '{batch_name}' created with {len(files)} files",
            "batch_job_id": str(batch_job.id),
            "status": "processing",
            "files_count": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "status_url": f"/api/v1/batch/status/{batch_job.id}",
        }

    except Exception as e:
        logger.error(f"Error creating batch job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch job: {str(e)}",
        )


async def process_batch_background(batch_job_id: UUID):
    """Process batch job in background with its own DB session."""
    try:
        from src.db.session import SessionLocal
        from src.services.batch_processing_service import BatchProcessingService
        
        # Create a new database session for background processing
        async with SessionLocal() as db:
            batch_service = BatchProcessingService(db)
            await batch_service.process_batch_job(batch_job_id)
        
        logger.info(f"Completed background processing for batch job {batch_job_id}")
    
    except Exception as e:
        logger.error(f"Error in background batch processing: {e}", exc_info=True)


@router.get("/status/{batch_job_id}")
async def get_batch_status(
    batch_job_id: UUID, user: CurrentUser = None, db: DatabaseSession = None
):
    """Get status of a batch job with detailed file results."""
    try:
        from sqlalchemy import select
        from src.models.batch_job import BatchFile
        
        batch_service = BatchProcessingService(db)
        batch_job = await batch_service.get_batch_job(batch_job_id, user.id)

        if not batch_job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch job not found")

        # Get detailed batch file results
        result = await db.execute(
            select(BatchFile).where(BatchFile.batch_job_id == batch_job_id)
        )
        batch_files = result.scalars().all()
        
        # Format file results
        file_results = [
            {
                "id": str(bf.id),
                "filename": bf.filename,
                "status": bf.status,
                "progress": bf.progress,
                "size": bf.file_size,
                "content_type": bf.content_type,
                "result": bf.result,
                "error": bf.error,
                "current_step": bf.current_step,
            }
            for bf in batch_files
        ]

        return {
            "batch_job_id": str(batch_job.id),
            "name": batch_job.name,
            "status": batch_job.status,
            "progress": batch_job.progress,
            "total_files": batch_job.total_files,
            "processed_files": batch_job.processed_files,
            "failed_files": batch_job.failed_files,
            "estimated_cost": batch_job.estimated_cost,
            "actual_cost": batch_job.actual_cost,
            "created_at": batch_job.created_at.isoformat(),
            "files": file_results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get batch status"
        )


@router.get("/jobs")
async def list_batch_jobs(
    limit: int = 20, offset: int = 0, user: CurrentUser = None, db: DatabaseSession = None
):
    """List user's batch jobs."""
    try:
        batch_service = BatchProcessingService(db)
        batch_jobs = await batch_service.get_user_batch_jobs(
            user_id=user.id, limit=limit, offset=offset
        )

        return {
            "batch_jobs": [
                {
                    "id": str(job.id),
                    "name": job.name,
                    "status": job.status,
                    "progress": job.progress,
                    "total_files": job.total_files,
                    "processed_files": job.processed_files,
                    "failed_files": job.failed_files,
                    "created_at": job.created_at.isoformat(),
                }
                for job in batch_jobs
            ],
            "total": len(batch_jobs),
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        logger.error(f"Error listing batch jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list batch jobs"
        )


@router.delete("/jobs/{batch_job_id}")
async def delete_batch_job(
    batch_job_id: UUID, user: CurrentUser = None, db: DatabaseSession = None
):
    """Delete a batch job."""
    try:
        batch_service = BatchProcessingService(db)
        batch_job = await batch_service.get_batch_job(batch_job_id, user.id)

        if not batch_job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch job not found")

        # Delete from database (cascade will handle batch files)
        await db.delete(batch_job)
        await db.commit()

        # Remove from queue if pending
        await job_queue.remove_job(f"batch_job:{batch_job_id}")

        return {"message": f"Batch job '{batch_job.name}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting batch job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete batch job"
        )
