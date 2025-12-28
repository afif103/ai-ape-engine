"""Redis-based job queue for batch processing."""

import json
import logging
from typing import Any, Dict, Optional
from uuid import UUID

import redis.asyncio as redis

from src.config import get_settings

logger = logging.getLogger(__name__)


class JobQueue:
    """Redis-based job queue for batch processing."""

    def __init__(self):
        self.settings = get_settings()
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = redis.Redis(
                host=self.settings.redis_url.split("://")[1].split(":")[0]
                if "://" in self.settings.redis_url
                else "localhost",
                port=int(self.settings.redis_url.split(":")[-1])
                if ":" in self.settings.redis_url
                else 6379,
                decode_responses=True,
            )
        return self.redis

    async def enqueue_batch_job(self, batch_job_id: UUID, priority: int = 1) -> str:
        """Enqueue a batch job for processing.

        Args:
            batch_job_id: ID of the batch job
            priority: Job priority (higher = more urgent)

        Returns:
            Job ID in the queue
        """
        redis_client = await self.connect()

        job_data = {
            "type": "batch_processing",
            "batch_job_id": str(batch_job_id),
            "priority": priority,
            "created_at": json.dumps(None, default=str),  # Will be set by Redis
        }

        # Use priority as score in sorted set
        job_id = f"batch_job:{batch_job_id}"
        await redis_client.zadd("batch_jobs_queue", {job_id: priority})

        # Store job data
        await redis_client.set(f"job_data:{job_id}", json.dumps(job_data))

        logger.info(f"Enqueued batch job {batch_job_id} with priority {priority}")
        return job_id

    async def dequeue_batch_job(self) -> Optional[Dict[str, Any]]:
        """Dequeue the highest priority batch job.

        Returns:
            Job data dictionary or None if queue is empty
        """
        redis_client = await self.connect()

        # Get the highest priority job (lowest score)
        result = await redis_client.zpopmin("batch_jobs_queue", 1)

        if not result:
            return None

        job_id = result[0][0]

        # Get job data
        job_data_str = await redis_client.get(f"job_data:{job_id}")
        if not job_data_str:
            logger.error(f"Job data not found for {job_id}")
            return None

        job_data = json.loads(job_data_str)
        job_data["job_id"] = job_id

        logger.info(f"Dequeued batch job {job_data.get('batch_job_id')}")
        return job_data

    async def get_queue_length(self) -> int:
        """Get the number of jobs in the queue.

        Returns:
            Number of jobs in queue
        """
        redis_client = await self.connect()
        return await redis_client.zcard("batch_jobs_queue")

    async def get_pending_jobs(self) -> list:
        """Get all pending jobs in the queue.

        Returns:
            List of job data dictionaries
        """
        redis_client = await self.connect()

        # Get all jobs with their scores
        jobs = await redis_client.zrange("batch_jobs_queue", 0, -1, withscores=True)

        pending_jobs = []
        for job_id, score in jobs:
            job_data_str = await redis_client.get(f"job_data:{job_id}")
            if job_data_str:
                job_data = json.loads(job_data_str)
                job_data["job_id"] = job_id
                job_data["priority"] = score
                pending_jobs.append(job_data)

        return pending_jobs

    async def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue.

        Args:
            job_id: Job ID to remove

        Returns:
            True if job was removed, False otherwise
        """
        redis_client = await self.connect()

        # Remove from queue
        removed_from_queue = await redis_client.zrem("batch_jobs_queue", job_id)

        # Remove job data
        removed_data = await redis_client.delete(f"job_data:{job_id}")

        success = removed_from_queue > 0 and removed_data > 0
        if success:
            logger.info(f"Removed job {job_id} from queue")
        else:
            logger.warning(f"Failed to remove job {job_id} from queue")

        return success

    async def update_job_priority(self, job_id: str, new_priority: int) -> bool:
        """Update the priority of a job in the queue.

        Args:
            job_id: Job ID to update
            new_priority: New priority value

        Returns:
            True if priority was updated, False otherwise
        """
        redis_client = await self.connect()

        # Update priority (score) in sorted set
        updated = await redis_client.zadd("batch_jobs_queue", {job_id: new_priority}, xx=True)

        if updated:
            logger.info(f"Updated priority of job {job_id} to {new_priority}")

        return updated > 0

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None


# Global instance
job_queue = JobQueue()
