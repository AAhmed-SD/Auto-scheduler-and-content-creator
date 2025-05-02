import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from .logging_config import loggers
from .scheduler import scheduler

logger = loggers["root"]


class Worker:
    def __init__(self):
        self.running = False
        self.poll_interval = 60  # seconds

    async def process_job(self, job: Dict[str, Any]) -> None:
        """Process a single job"""
        try:
            job_id = job["id"]
            logger.info(f"Processing job: {job_id}")

            # Update job status to processing
            await scheduler.update_job_status(job_id, "processing")

            # TODO: Implement actual job processing logic
            # This is where you'd add your specific job handling code
            # For example:
            # - Posting to social media
            # - Processing content
            # - Sending notifications

            # Simulate job processing
            await asyncio.sleep(2)

            # Update job status to completed
            await scheduler.update_job_status(
                job_id, "completed", {"processed_at": datetime.now().isoformat()}
            )

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            await scheduler.retry_job(job_id, str(e))

    async def run(self) -> None:
        """Run the worker"""
        self.running = True
        logger.info("Worker started")

        while self.running:
            try:
                # Get next job
                job = await scheduler.get_next_job()

                if job:
                    # Process job
                    await self.process_job(job)
                else:
                    # No jobs, wait before checking again
                    await asyncio.sleep(self.poll_interval)

                # Cleanup old jobs
                await scheduler.cleanup_old_jobs()

            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(self.poll_interval)

    async def stop(self) -> None:
        """Stop the worker"""
        self.running = False
        logger.info("Worker stopped")


# Create global worker instance
worker = Worker()
