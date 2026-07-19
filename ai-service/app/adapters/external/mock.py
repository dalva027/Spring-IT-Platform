import uuid
from typing import Any

from sqlalchemy import func, select

from app.adapters.external.base import ExternalTracker
from app.db.models import ExternalIssue
from app.db.session import session_factory

_KEY_PREFIX = {"jira": "HD", "servicenow": "INC", "freshdesk": "FD"}
_URL_TEMPLATE = {
    "jira": "https://jira.internal.example/browse/{key}",
    "servicenow": "https://servicenow.internal.example/incident/{key}",
    "freshdesk": "https://freshdesk.internal.example/a/tickets/{key}",
}


class MockExternalTracker(ExternalTracker):
    def __init__(self, provider: str):
        if provider not in _KEY_PREFIX:
            raise ValueError(f"unknown provider {provider!r}")
        self.provider = provider

    async def create_issue(
        self, summary: str, description: str, request_id: str | None, ticket_id: int | None
    ) -> dict[str, Any]:
        async with session_factory()() as session:
            result = await session.execute(
                select(func.count()).select_from(ExternalIssue).where(
                    ExternalIssue.provider == self.provider
                )
            )
            # Realistic-looking sequential keys, e.g. HD-1042.
            key = f"{_KEY_PREFIX[self.provider]}-{1041 + int(result.scalar_one()) + 1}"
            url = _URL_TEMPLATE[self.provider].format(key=key)
            session.add(
                ExternalIssue(
                    provider=self.provider,
                    external_key=key,
                    request_id=uuid.UUID(request_id) if request_id else None,
                    ticket_id=ticket_id,
                    summary=summary[:512],
                    url=url,
                    payload={"description": description[:2000]},
                )
            )
            await session.commit()
        return {
            "provider": self.provider,
            "key": key,
            "url": url,
            "summary": summary[:512],
            "requestId": request_id,
            "ticketId": ticket_id,
        }
