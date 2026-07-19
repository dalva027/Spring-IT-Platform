"""Storage adapter seam: everything the pipeline persists goes through this
interface so the local Postgres implementation can be swapped for DynamoDB
without touching graph nodes or API routes."""

import uuid
from abc import ABC, abstractmethod
from typing import Any


class StorageAdapter(ABC):
    @abstractmethod
    async def create_analysis(
        self, request_id: uuid.UUID, channel: str, issue_text: str, user_id: int,
        ticket_id: int | None = None,
    ) -> None: ...

    @abstractmethod
    async def update_analysis(self, request_id: uuid.UUID, **fields: Any) -> None: ...

    @abstractmethod
    async def get_analysis(self, request_id: uuid.UUID) -> dict[str, Any] | None: ...

    @abstractmethod
    async def latest_analysis_for_ticket(self, ticket_id: int) -> dict[str, Any] | None: ...

    @abstractmethod
    async def append_event(
        self, request_id: uuid.UUID, event_type: str, node: str, payload: dict[str, Any] | None
    ) -> int: ...

    @abstractmethod
    async def list_events(self, request_id: uuid.UUID) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def record_external_issue(self, issue: dict[str, Any]) -> None: ...

    @abstractmethod
    async def record_notification(self, notification: dict[str, Any]) -> None: ...
