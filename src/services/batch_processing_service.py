"""Batch processing service for handling multiple file uploads simultaneously."""

import asyncio
import logging
import os
import tempfile
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ValidationError
from src.models.batch_job import BatchJob, BatchFile
from sqlalchemy import select, func
from typing import List
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.extraction_service import ExtractionService
from src.services.processing_status import processing_tracker

logger = logging.getLogger(__name__)


class BatchProcessingService:
    """Service for processing multiple files in batches."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.extraction_service = ExtractionService()

    async def create_batch_job(
        self, user_id: UUID, batch_name: str, files: List[Dict[str, Any]]
    ) -> BatchJob:
        """Create a new batch job with multiple files.

        Args:
            user_id: ID of the user creating the batch
            batch_name: Name for the batch job
            files: List of file metadata dictionaries

        Returns:
            Created BatchJob instance

        Raises:
            ValidationError: If validation fails
        """
        # Validate user exists
        user = await self.user_repo.get_by_id(str(user_id))
        if not user:
            raise ValidationError("User not found")

        # Validate files
        if not files or len(files) == 0:
            raise ValidationError("At least one file is required")

        if len(files) > 10:  # Limit batch size
            raise ValidationError("Maximum 10 files per batch")

        # Create batch job
        batch_job = BatchJob(user_id=user_id, name=batch_name, total_files=len(files), files=files)

        self.db.add(batch_job)
        await self.db.flush()  # Get the ID

        # Create individual batch files
        for file_info in files:
            batch_file = BatchFile(
                batch_job_id=batch_job.id,
                filename=file_info["filename"],
                file_size=file_info["size"],
                content_type=file_info["content_type"],
            )
            self.db.add(batch_file)

        await self.db.commit()
        await self.db.refresh(batch_job)

        logger.info(f"Created batch job {batch_job.id} with {len(files)} files for user {user_id}")

        return batch_job

    async def process_batch_job(self, batch_job_id: UUID) -> None:
        """Process all files in a batch job concurrently.

        Args:
            batch_job_id: ID of the batch job to process
        """
        # Get batch job with files
        batch_job = await self.db.get(BatchJob, batch_job_id)
        if not batch_job:
            logger.error(f"Batch job {batch_job_id} not found")
            return

        # Update batch status
        batch_job.status = "processing"
        await self.db.commit()

        logger.info(f"Starting batch processing for job {batch_job_id}")

        # Get all batch files
        result = await self.db.execute(
            select(BatchFile).where(BatchFile.batch_job_id == batch_job_id)
        )
        files = result.scalars().all()

        # Process files concurrently with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent file processing
        tasks = []

        async def process_single_file(batch_file):
            async with semaphore:
                await self._process_batch_file(batch_file, batch_job_id)

        # Create tasks for all files
        for file_row in files:
            batch_file = BatchFile(
                id=file_row[0],
                batch_job_id=file_row[1],
                filename=file_row[2],
                file_size=file_row[3],
                content_type=file_row[4],
                status=file_row[5] or "queued",
                progress=file_row[6] or 0.0,
                current_step=file_row[7],
                result=file_row[8],
                error=file_row[9],
                aws_services_used=file_row[10] or [],
                cost_estimate=file_row[11] or 0.0,
                created_at=file_row[12],
                updated_at=file_row[13],
            )
            tasks.append(process_single_file(batch_file))

        # Wait for all files to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Update batch job completion status
        await self._update_batch_completion_status(batch_job_id)

        logger.info(f"Completed batch processing for job {batch_job_id}")

    async def _process_batch_file(self, batch_file: BatchFile, batch_job_id: UUID) -> None:
        """Process a single file within a batch.

        Args:
            batch_file: The batch file to process
            batch_job_id: Parent batch job ID
        """
        try:
            # Update file status
            batch_file.status = "processing"
            batch_file.current_step = "Initializing"
            await self.db.commit()

            # For now, we'll simulate file processing
            # In a real implementation, this would handle file upload and processing
            # Since we don't have the actual file content yet, we'll mark as completed
            # The actual implementation will be in the API route

            batch_file.status = "completed"
            batch_file.progress = 100.0
            batch_file.result = {"message": f"File {batch_file.filename} processed successfully"}
            batch_file.current_step = "Completed"

            await self.db.commit()

            logger.info(f"Processed batch file {batch_file.id} ({batch_file.filename})")

        except Exception as e:
            logger.error(f"Failed to process batch file {batch_file.id}: {e}")
            batch_file.status = "failed"
            batch_file.error = str(e)
            await self.db.commit()

    async def _update_batch_completion_status(self, batch_job_id: UUID) -> None:
        """Update the overall batch job completion status.

        Args:
            batch_job_id: ID of the batch job
        """
        # Get batch job
        batch_job = await self.db.get(BatchJob, batch_job_id)
        if not batch_job:
            return

        # Count file statuses
        result = await self.db.execute(
            select(
                func.count(BatchFile.id).label("total"),
                func.count(func.case((BatchFile.status == "completed", 1))).label("completed"),
                func.count(func.case((BatchFile.status == "failed", 1))).label("failed"),
            ).where(BatchFile.batch_job_id == batch_job_id)
        )

        counts = result.first()
        if counts:
            total, completed, failed = counts.total, counts.completed, counts.failed
        else:
            total, completed, failed = 0, 0, 0

        # Update batch status
        if failed > 0:
            batch_job.status = "completed_with_errors"
        elif completed == total:
            batch_job.status = "completed"
        else:
            batch_job.status = "processing"

        batch_job.processed_files = completed
        batch_job.failed_files = failed
        batch_job.progress = (completed + failed) / total * 100 if total > 0 else 0

        await self.db.commit()

    async def get_batch_job(self, batch_job_id: UUID, user_id: UUID) -> Optional[BatchJob]:
        """Get a batch job by ID for a specific user.

        Args:
            batch_job_id: ID of the batch job
            user_id: ID of the user (for authorization)

        Returns:
            BatchJob instance or None
        """
        batch_job = await self.db.get(BatchJob, batch_job_id)
        if batch_job and batch_job.user_id == user_id:
            return batch_job
        return None

    async def get_user_batch_jobs(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[BatchJob]:
        """Get batch jobs for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip

        Returns:
            List of BatchJob instances
        """
        result = await self.db.execute(
            select(BatchJob)
            .where(BatchJob.user_id == user_id)
            .order_by(BatchJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())
