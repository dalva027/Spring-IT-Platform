"""External issue-tracker seam (Jira / ServiceNow / Freshdesk). The local
implementation persists realistic fake issues; a real integration would call
the vendor API behind the same interface."""

from abc import ABC, abstractmethod
from typing import Any


class ExternalTracker(ABC):
    provider: str

    @abstractmethod
    async def create_issue(
        self, summary: str, description: str, request_id: str | None, ticket_id: int | None
    ) -> dict[str, Any]:
        """Returns {provider, key, url, summary, requestId, ticketId}."""
