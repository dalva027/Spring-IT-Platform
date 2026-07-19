import time
import uuid
from typing import Any

import jwt
import pytest

from app.config import get_settings


def make_token(
    user_id: int = 1, email: str = "user@helpdesk.local", role: str = "REQUESTER"
) -> str:
    settings = get_settings()
    now = int(time.time())
    return jwt.encode(
        {"sub": str(user_id), "email": email, "role": role, "iat": now, "exp": now + 300},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


@pytest.fixture
def employee_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token()}"}


@pytest.fixture
def agent_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(user_id=2, role='AGENT')}"}


class FakeStorage:
    """In-memory StorageAdapter double used by unit and integration tests."""

    def __init__(self) -> None:
        self.analyses: dict[uuid.UUID, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.notifications: list[dict[str, Any]] = []
        self.external_issues: list[dict[str, Any]] = []

    async def create_analysis(self, request_id, channel, issue_text, user_id, ticket_id=None):
        self.analyses[request_id] = {
            "requestId": str(request_id),
            "channel": channel,
            "status": "RUNNING",
            "issueText": issue_text,
            "userId": user_id,
            "ticketId": ticket_id,
            "errors": None,
        }

    async def update_analysis(self, request_id, **fields):
        analysis = self.analyses.setdefault(request_id, {"requestId": str(request_id)})
        for key, value in fields.items():
            camel = {
                "ticket_id": "ticketId",
                "doc_hits": "docHits",
                "ticket_hits": "ticketHits",
                "external_issues": "externalIssues",
                "issue_text": "issueText",
            }.get(key, key)
            analysis[camel] = value

    async def get_analysis(self, request_id):
        return self.analyses.get(request_id)

    async def latest_analysis_for_ticket(self, ticket_id):
        for analysis in reversed(list(self.analyses.values())):
            if analysis.get("ticketId") == ticket_id:
                return analysis
        return None

    async def append_event(self, request_id, event_type, node, payload):
        self.events.append(
            {
                "requestId": str(request_id),
                "eventType": event_type,
                "node": node,
                "payload": payload,
            }
        )
        return len(self.events)

    async def list_events(self, request_id):
        return [e for e in self.events if e["requestId"] == str(request_id)]

    async def record_external_issue(self, issue):
        self.external_issues.append(issue)

    async def record_notification(self, notification):
        self.notifications.append(notification)


@pytest.fixture
def fake_storage() -> FakeStorage:
    return FakeStorage()
