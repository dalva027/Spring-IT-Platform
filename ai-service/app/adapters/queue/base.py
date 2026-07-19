"""Queue adapter seam: local implementation is a jobs table polled by an
in-process asyncio worker; on AWS the same interface maps to SQS + Lambda."""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

JobHandler = Callable[[dict[str, Any]], Awaitable[None]]


class QueueAdapter(ABC):
    @abstractmethod
    async def enqueue(self, job_type: str, payload: dict[str, Any]) -> None: ...

    @abstractmethod
    def register_handler(self, job_type: str, handler: JobHandler) -> None: ...
