"""Scheduler configuration module."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.logging_config import loggers
from app.core.redis_config import redis

logger = loggers.get_logger(__name__)


class Scheduler:
    """Scheduler class for managing scheduled tasks."""

    def __init__(self):
        """Initialize scheduler."""
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.redis = redis
        self.queue_key = "scheduler:queue"
        self.retry_key = "scheduler:retries"
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes

    async def start(self):
        """Start the scheduler."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        """Stop the scheduler."""
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
                self._task = None

    async def _run(self):
        """Run the scheduler loop."""
        while self._running:
            now = datetime.now()
            for task_id, task in list(self._tasks.items()):
                if task["next_run"] <= now:
                    asyncio.create_task(self._execute_task(task_id))
                    if task["repeat"]:
                        task["next_run"] = now + task["interval"]
                    else:
                        del self._tasks[task_id]
            await asyncio.sleep(1)

    async def _execute_task(self, task_id: str):
        """Execute a scheduled task."""
        task = self._tasks[task_id]
        try:
            await task["callback"](*task["args"], **task["kwargs"])
        except Exception as e:
            logger.error("Error executing task %s: %s", task_id, str(e))

    def schedule_task(
        self,
        task_id: str,
        callback: Any,
        run_at: datetime,
        *args: Any,
        repeat: bool = False,
        interval: Optional[timedelta] = None,
        **kwargs: Any,
    ) -> bool:
        """Schedule a task."""
        if task_id in self._tasks:
            return False
        self._tasks[task_id] = {
            "callback": callback,
            "next_run": run_at,
            "repeat": repeat,
            "interval": interval,
            "args": args,
            "kwargs": kwargs,
        }
        return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        return bool(self._tasks.pop(task_id, None))

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all scheduled tasks."""
        return [
            {
                "id": task_id,
                "next_run": task["next_run"],
                "repeat": task["repeat"],
                "interval": task["interval"],
            }
            for task_id, task in self._tasks.items()
        ]

    async def schedule_job(
        self, job_data: Dict[str, Any], scheduled_time: datetime
    ) -> str:
        """Schedule a new job"""
        try:
            job_id = f"job:{datetime.now().timestamp()}"
            job = {
                "id": job_id,
                "data": job_data,
                "scheduled_time": scheduled_time.isoformat(),
                "status": "pending",
                "retries": 0,
                "created_at": datetime.now().isoformat(),
            }

            # Add to scheduled queue
            await self.redis.set(f"{self.queue_key}:{job_id}", job)

            # Add to sorted set for scheduling
            score = scheduled_time.timestamp()
            await self.redis.zadd(self.queue_key, {job_id: score})

            logger.info(f"Job scheduled: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Error scheduling job: {str(e)}")
            raise

    async def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get next due job"""
        try:
            # Get jobs due now or earlier
            now = datetime.now().timestamp()
            job_ids = await self.redis.zrangebyscore(
                self.queue_key, 0, now, start=0, num=1
            )

            if not job_ids:
                return None

            job_id = job_ids[0]
            job = await self.redis.get(f"{self.queue_key}:{job_id}")

            if job:
                # Remove from queue
                await self.redis.zrem(self.queue_key, job_id)
                return job

            return None

        except Exception as e:
            logger.error(f"Error getting next job: {str(e)}")
            return None

    async def retry_job(self, job_id: str, error: str) -> bool:
        """Retry a failed job"""
        try:
            job = await self.redis.get(f"{self.queue_key}:{job_id}")
            if not job:
                return False

            job["retries"] += 1
            job["last_error"] = error
            job["status"] = "retrying"

            if job["retries"] >= self.max_retries:
                job["status"] = "failed"
                await self.redis.set(f"{self.queue_key}:{job_id}", job)
                return False

            # Schedule retry
            retry_time = datetime.now() + timedelta(seconds=self.retry_delay)
            score = retry_time.timestamp()
            await self.redis.zadd(self.queue_key, {job_id: score})
            await self.redis.set(f"{self.queue_key}:{job_id}", job)

            logger.info(f"Job retry scheduled: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Error retrying job: {str(e)}")
            return False

    async def update_job_status(
        self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update job status"""
        try:
            job = await self.redis.get(f"{self.queue_key}:{job_id}")
            if not job:
                return False

            job["status"] = status
            if result:
                job["result"] = result

            await self.redis.set(f"{self.queue_key}:{job_id}", job)
            logger.info(f"Job status updated: {job_id} -> {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            return False

    async def cleanup_old_jobs(self, days: int = 7) -> int:
        """Cleanup old completed jobs"""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).timestamp()
            old_jobs = await self.redis.zrangebyscore(self.queue_key, 0, cutoff)

            for job_id in old_jobs:
                job = await self.redis.get(f"{self.queue_key}:{job_id}")
                if job and job["status"] in ["completed", "failed"]:
                    await self.redis.delete(f"{self.queue_key}:{job_id}")
                    await self.redis.zrem(self.queue_key, job_id)

            return len(old_jobs)

        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {str(e)}")
            return 0


# Create global scheduler instance
scheduler = Scheduler()
