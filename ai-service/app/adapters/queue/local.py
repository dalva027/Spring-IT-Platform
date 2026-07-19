import asyncio
import logging
from datetime import timedelta
from typing import Any

from sqlalchemy import select

from app.adapters.queue.base import JobHandler, QueueAdapter
from app.config import get_settings
from app.db.models import Job, utcnow
from app.db.session import session_factory

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


class DbJobQueue(QueueAdapter):
    def __init__(self) -> None:
        self._handlers: dict[str, JobHandler] = {}
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()

    def register_handler(self, job_type: str, handler: JobHandler) -> None:
        self._handlers[job_type] = handler

    async def enqueue(self, job_type: str, payload: dict[str, Any]) -> None:
        async with session_factory()() as session:
            session.add(Job(type=job_type, payload=payload))
            await session.commit()

    def start_worker(self) -> None:
        if self._task is None:
            self._stopping.clear()
            self._task = asyncio.create_task(self._run(), name="job-queue-worker")

    async def stop_worker(self) -> None:
        self._stopping.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        interval = get_settings().queue_poll_interval_seconds
        while not self._stopping.is_set():
            try:
                worked = await self._poll_once()
            except Exception:
                logger.exception("job worker poll failed")
                worked = False
            if not worked:
                await asyncio.sleep(interval)

    async def _poll_once(self) -> bool:
        """Claim and run one due job. Returns True if a job was processed."""
        async with session_factory()() as session:
            result = await session.execute(
                select(Job)
                .where(Job.status == "PENDING", Job.run_after <= utcnow())
                .order_by(Job.id)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            job = result.scalar_one_or_none()
            if job is None:
                return False
            job.status = "RUNNING"
            job.attempts += 1
            job_id, job_type, payload, attempts = job.id, job.type, job.payload, job.attempts
            await session.commit()

        handler = self._handlers.get(job_type)
        error: str | None = None
        if handler is None:
            error = f"no handler registered for job type {job_type!r}"
        else:
            try:
                await handler(payload)
            except Exception as exc:  # noqa: BLE001 — job failures must not kill the worker
                logger.exception("job %s (%s) failed", job_id, job_type)
                error = str(exc)[:2000]

        async with session_factory()() as session:
            job = await session.get(Job, job_id)
            if job is None:
                return True
            if error is None:
                job.status = "DONE"
                job.last_error = ""
            elif attempts >= MAX_ATTEMPTS:
                job.status = "FAILED"
                job.last_error = error
            else:
                job.status = "PENDING"
                job.last_error = error
                job.run_after = utcnow() + timedelta(seconds=10 * attempts)
            await session.commit()
        return True
