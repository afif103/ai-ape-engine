"""Processing status API endpoints for real-time updates."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.dependencies import CurrentUser
from src.services.processing_status import processing_tracker

router = APIRouter(prefix="/processing", tags=["processing"])


@router.get("/status/{job_id}")
async def get_processing_status(job_id: str, user: CurrentUser):
    """Get processing status for a specific job."""
    job = processing_tracker.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Processing job {job_id} not found"
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=job.to_dict())


@router.get("/status")
async def get_all_processing_status(user: CurrentUser):
    """Get all processing jobs status."""
    jobs = processing_tracker.get_all_jobs()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "jobs": jobs,
            "total_jobs": len(jobs),
            "active_jobs": len(processing_tracker.get_active_jobs()),
        },
    )


@router.get("/active")
async def get_active_processing_jobs(user: CurrentUser):
    """Get only active processing jobs."""
    active_jobs = processing_tracker.get_active_jobs()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"active_jobs": active_jobs, "count": len(active_jobs)},
    )


@router.delete("/status/{job_id}")
async def cancel_processing_job(job_id: str, user: CurrentUser):
    """Cancel a processing job (if still queued/processing)."""
    job = processing_tracker.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Processing job {job_id} not found"
        )

    if job.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status}",
        )

    # Mark as failed/cancelled
    processing_tracker.fail_job(job_id, "Cancelled by user")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Processing job {job_id} cancelled", "job_id": job_id},
    )
