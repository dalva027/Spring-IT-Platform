"""api_agent channel behavior with a mocked ticket client / notifiers / trackers."""

import pytest

from app.graph.nodes import api_agent as api_agent_module
from app.graph.nodes.api_agent import api_agent


class FakeTicketClient:
    def __init__(self):
        self.created = []
        self.comments = []

    async def create_ticket(self, token, title, description, priority):
        self.created.append({"token": token, "title": title, "priority": priority})
        return {"id": 101, "title": title, "priority": priority}

    async def add_comment(self, token, ticket_id, body):
        self.comments.append({"token": token, "ticketId": ticket_id, "body": body})
        return {"id": 1, "ticketId": ticket_id, "body": body}


class FakeNotifier:
    channel = "fake"

    def __init__(self):
        self.sent = []

    async def send(self, subject, body, recipient=""):
        self.sent.append({"subject": subject, "body": body})
        return {"channel": self.channel, "subject": subject, "body": body, "status": "SENT"}


class FakeTracker:
    def __init__(self, provider):
        self.provider = provider

    async def create_issue(self, summary, description, request_id, ticket_id):
        return {
            "provider": self.provider,
            "key": f"{self.provider.upper()}-1",
            "url": "https://example.test",
            "summary": summary,
            "requestId": request_id,
            "ticketId": ticket_id,
        }


class FakeStorageNoop:
    async def record_notification(self, record):
        pass


@pytest.fixture
def wire(monkeypatch):
    client = FakeTicketClient()
    notifier = FakeNotifier()
    monkeypatch.setattr(api_agent_module, "get_ticket_client", lambda: client)
    monkeypatch.setattr(api_agent_module, "get_notifiers", lambda: [notifier])
    monkeypatch.setattr(api_agent_module, "get_tracker", lambda provider: FakeTracker(provider))
    monkeypatch.setattr(api_agent_module, "get_storage", lambda: FakeStorageNoop())
    monkeypatch.setattr(api_agent_module, "mint_service_token", lambda: "service-token")
    return client, notifier


def assistant_state(**overrides):
    state = {
        "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "channel": "assistant",
        "user": {"id": 1, "email": "user@helpdesk.local", "role": "REQUESTER"},
        "user_token": "employee-token",
        "issue_text": "VPN keeps dropping when I work from home",
        "classification": {"category": "NETWORKING", "suggested_priority": "HIGH"},
        "escalation": {
            "outcome": "NEEDS_TECHNICIAN",
            "ticket_priority": "HIGH",
            "assignment_hint": "Network team",
        },
        "troubleshooting": {"steps": ["Restart the client"], "self_serviceable": False},
        "errors": [],
    }
    state.update(overrides)
    return state


async def test_assistant_creates_ticket_with_employee_token(wire):
    client, notifier = wire
    update = await api_agent(assistant_state())

    assert update["ticket_id"] == 101
    assert client.created[0]["token"] == "employee-token"
    assert client.created[0]["priority"] == "HIGH"
    # AI comment is authored via the service token.
    assert client.comments[0]["token"] == "service-token"
    assert client.comments[0]["ticketId"] == 101
    # NETWORKING → mock jira issue.
    assert update["external_issues"][0]["provider"] == "jira"
    assert notifier.sent  # assistant runs always notify


async def test_assistant_emergency_uses_critical_priority(wire):
    client, _ = wire
    state = assistant_state(
        escalation={"outcome": "EMERGENCY", "ticket_priority": "CRITICAL", "assignment_hint": ""},
        classification={"category": "IT", "suggested_priority": "LOW"},
    )
    update = await api_agent(state)
    assert client.created[0]["priority"] == "CRITICAL"
    # EMERGENCY without a NETWORKING/SECURITY category still opens an external issue.
    assert update["external_issues"][0]["provider"] == "freshdesk"


async def test_ticket_event_never_creates_ticket(wire):
    client, notifier = wire
    state = assistant_state(channel="ticket_event", existing_ticket_id=55)
    update = await api_agent(state)

    assert client.created == []
    assert update["ticket_id"] == 55
    assert client.comments[0]["ticketId"] == 55
    assert update["external_issues"] == []  # external issues are assistant-only
    assert notifier.sent == []  # non-emergency ticket events stay quiet


async def test_ticket_event_emergency_notifies(wire):
    _, notifier = wire
    state = assistant_state(
        channel="ticket_event",
        existing_ticket_id=55,
        escalation={"outcome": "EMERGENCY", "ticket_priority": "CRITICAL", "assignment_hint": ""},
    )
    await api_agent(state)
    assert notifier.sent


async def test_ticket_creation_failure_is_reported_not_fatal(wire, monkeypatch):
    client, _ = wire

    async def failing_create(token, title, description, priority):
        raise RuntimeError("ticket-service down")

    monkeypatch.setattr(client, "create_ticket", failing_create)
    update = await api_agent(assistant_state())
    assert update["ticket_id"] is None
    assert any("ticket creation failed" in error for error in update["errors"])
