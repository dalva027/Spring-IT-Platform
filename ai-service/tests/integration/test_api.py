"""Integration tests over the ASGI app with the graph and storage stubbed —
no Postgres or Gemini needed. Verifies auth handling, the analyze flow, and
SSE frame ordering."""

import httpx
import pytest

from app.api import routes_analyze, routes_assist
from app.graph import runner
from app.main import app


@pytest.fixture
def client():
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://ai-service.test")


@pytest.fixture
def stub_assist(monkeypatch, fake_storage):
    monkeypatch.setattr(routes_assist, "get_storage", lambda: fake_storage)

    async def fake_stream(initial_state, request_id):
        yield {"type": "node_start", "node": "classify", "payload": {"label": "Classifying"}}
        yield {
            "type": "node_end",
            "node": "classify",
            "payload": {"classification": {"category": "NETWORKING"}},
        }
        yield {"type": "result", "node": "", "payload": {"requestId": str(request_id),
                                                          "status": "COMPLETED"}}

    monkeypatch.setattr(runner, "stream_pipeline", fake_stream)
    return fake_storage


async def test_assist_stream_requires_auth(client, stub_assist):
    async with client:
        response = await client.post("/api/assist/stream", json={"issue_text": "vpn is broken"})
    assert response.status_code == 401


async def test_assist_stream_frame_ordering(client, stub_assist, employee_headers):
    async with client:
        response = await client.post(
            "/api/assist/stream",
            json={"issue_text": "My VPN disconnects every 10 minutes"},
            headers=employee_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert response.headers["x-accel-buffering"] == "no"
        body = response.text

    events = [
        line.removeprefix("event: ")
        for line in body.splitlines()
        if line.startswith("event: ")
    ]
    # started must come first, then pipeline frames in order, result last.
    assert events == ["started", "node_start", "node_end", "result"]
    # The analysis row was created before streaming began.
    assert len(stub_assist.analyses) == 1


async def test_analyze_enqueues_job_with_employee_token(
    client, monkeypatch, fake_storage, employee_headers
):
    enqueued = []

    class FakeQueue:
        async def enqueue(self, job_type, payload):
            enqueued.append((job_type, payload))

    monkeypatch.setattr(routes_analyze, "get_storage", lambda: fake_storage)
    monkeypatch.setattr(routes_analyze, "get_queue", lambda: FakeQueue())

    async with client:
        response = await client.post("/api/analyze/tickets/42", headers=employee_headers)
    assert response.status_code == 202
    job_type, payload = enqueued[0]
    assert job_type == "analyze_ticket"
    assert payload["ticketId"] == 42
    # The job carries the employee's own JWT for pass-through calls.
    assert payload["token"] == employee_headers["Authorization"].removeprefix("Bearer ")


async def test_analysis_by_ticket_404_when_missing(
    client, monkeypatch, fake_storage, employee_headers
):
    monkeypatch.setattr(routes_analyze, "get_storage", lambda: fake_storage)
    async with client:
        response = await client.get("/api/analyses/by-ticket/999", headers=employee_headers)
    assert response.status_code == 404


async def test_admin_routes_require_agent_role(client, employee_headers):
    async with client:
        response = await client.post("/api/admin/index-tickets", headers=employee_headers)
    assert response.status_code == 403


async def test_healthz(client):
    async with client:
        response = await client.get("/healthz")
    assert response.status_code == 200
