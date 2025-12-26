"""Processing status tracking for real-time updates."""

import time
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ProcessingStatus:
    """Processing status for file extraction."""

    job_id: str
    file_name: str
    file_size: int
    status: str  # 'queued', 'processing', 'completed', 'failed'
    progress: int  # 0-100
    current_step: str
    start_time: float
    end_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    aws_services_used: list = None
    cost_estimate: float = 0.0

    def __post_init__(self):
        if self.aws_services_used is None:
            self.aws_services_used = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        data = asdict(self)
        # Convert timestamps to readable format
        data["start_time"] = datetime.fromtimestamp(self.start_time).isoformat()
        if self.end_time:
            data["end_time"] = datetime.fromtimestamp(self.end_time).isoformat()
            data["duration"] = self.end_time - self.start_time
        return data

    def update_progress(self, progress: int, step: str):
        """Update processing progress."""
        self.progress = progress
        self.current_step = step

    def complete(self, result: Dict[str, Any] = None):
        """Mark processing as completed."""
        self.status = "completed"
        self.progress = 100
        self.end_time = time.time()
        self.result = result

    def fail(self, error: str):
        """Mark processing as failed."""
        self.status = "failed"
        self.end_time = time.time()
        self.error = error


class ProcessingStatusTracker:
    """Tracks processing status for multiple jobs."""

    def __init__(self):
        self.jobs: Dict[str, ProcessingStatus] = {}
        self.max_jobs = 100  # Keep only recent jobs

    def create_job(self, file_name: str, file_size: int) -> str:
        """Create a new processing job."""
        job_id = str(uuid.uuid4())
        job = ProcessingStatus(
            job_id=job_id,
            file_name=file_name,
            file_size=file_size,
            status="queued",
            progress=0,
            current_step="Initializing",
            start_time=time.time(),
        )
        self.jobs[job_id] = job

        # Clean up old jobs if we have too many
        if len(self.jobs) > self.max_jobs:
            oldest_job_id = min(self.jobs.keys(), key=lambda x: self.jobs[x].start_time)
            del self.jobs[oldest_job_id]

        return job_id

    def get_job(self, job_id: str) -> Optional[ProcessingStatus]:
        """Get job status by ID."""
        return self.jobs.get(job_id)

    def update_job(
        self, job_id: str, progress: int, step: str, aws_service: str = None, cost_add: float = 0.0
    ):
        """Update job progress."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.update_progress(progress, step)
            job.status = "processing"
            if aws_service and aws_service not in job.aws_services_used:
                job.aws_services_used.append(aws_service)
            job.cost_estimate += cost_add

    def complete_job(self, job_id: str, result: Dict[str, Any] = None):
        """Mark job as completed."""
        if job_id in self.jobs:
            self.jobs[job_id].complete(result)

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed."""
        if job_id in self.jobs:
            self.jobs[job_id].fail(error)

    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get all jobs as dictionaries."""
        return {job_id: job.to_dict() for job_id, job in self.jobs.items()}

    def get_active_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get only active (non-completed) jobs."""
        return {
            job_id: job.to_dict()
            for job_id, job in self.jobs.items()
            if job.status in ["queued", "processing"]
        }


# Global instance
processing_tracker = ProcessingStatusTracker()
