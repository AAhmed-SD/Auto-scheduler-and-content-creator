import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from .redis_config import redis
from .logging_config import loggers

logger = loggers['root']

class Scheduler:
    def __init__(self):
        self.redis = redis
        self.queue_key = 'scheduler:queue'
        self.retry_key = 'scheduler:retries'
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes

    async def schedule_job(self, job_data: Dict[str, Any], scheduled_time: datetime) -> str:
        """Schedule a new job"""
        try:
            job_id = f"job:{datetime.now().timestamp()}"
            job = {
                'id': job_id,
                'data': job_data,
                'scheduled_time': scheduled_time.isoformat(),
                'status': 'pending',
                'retries': 0,
                'created_at': datetime.now().isoformat()
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
            job_ids = await self.redis.zrangebyscore(self.queue_key, 0, now, start=0, num=1)

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

            job['retries'] += 1
            job['last_error'] = error
            job['status'] = 'retrying'

            if job['retries'] >= self.max_retries:
                job['status'] = 'failed'
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

    async def update_job_status(self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Update job status"""
        try:
            job = await self.redis.get(f"{self.queue_key}:{job_id}")
            if not job:
                return False

            job['status'] = status
            if result:
                job['result'] = result

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
                if job and job['status'] in ['completed', 'failed']:
                    await self.redis.delete(f"{self.queue_key}:{job_id}")
                    await self.redis.zrem(self.queue_key, job_id)

            return len(old_jobs)

        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {str(e)}")
            return 0

# Create global scheduler instance
scheduler = Scheduler() 