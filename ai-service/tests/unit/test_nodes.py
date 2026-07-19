"""Unit tests for LLM nodes with a fake structured_call (no network)."""

import pytest

from app.graph import llm
from app.graph.builder import route_after_escalate
from app.graph.nodes.classify import Classification, classify
from app.graph.nodes.escalate import Escalation, escalate
from app.graph.nodes.troubleshoot import Troubleshooting, troubleshoot


def fake_structured(result_by_schema: dict):
    async def _call(schema, prompt):
        return result_by_schema.get(schema)

    return _call


@pytest.fixture
def base_state():
    return {"issue_text": "My VPN drops every 10 minutes", "channel": "assistant", "errors": []}


async def test_classify_parses_llm_output(monkeypatch, base_state):
    monkeypatch.setattr(
        llm,
        "structured_call",
        fake_structured(
            {
                Classification: Classification(
                    category="NETWORKING",
                    suggested_priority="HIGH",
                    confidence=0.92,
                    rationale="VPN connectivity issue",
                )
            }
        ),
    )
    update = await classify(base_state)
    assert update["classification"]["category"] == "NETWORKING"
    assert update["classification"]["suggested_priority"] == "HIGH"
    assert "errors" not in update


async def test_classify_falls_back_when_llm_fails(monkeypatch, base_state):
    monkeypatch.setattr(llm, "structured_call", fake_structured({}))
    update = await classify(base_state)
    assert update["classification"]["category"] == "IT"
    assert update["classification"]["suggested_priority"] == "MEDIUM"
    assert update["errors"]


async def test_troubleshoot_falls_back(monkeypatch, base_state):
    monkeypatch.setattr(llm, "structured_call", fake_structured({}))
    update = await troubleshoot(base_state)
    assert update["troubleshooting"]["steps"]
    assert update["troubleshooting"]["self_serviceable"] is False


async def test_escalate_forces_critical_on_emergency(monkeypatch, base_state):
    monkeypatch.setattr(
        llm,
        "structured_call",
        fake_structured(
            {
                Escalation: Escalation(
                    outcome="EMERGENCY", ticket_priority="LOW", assignment_hint="Security team"
                )
            }
        ),
    )
    update = await escalate(base_state)
    assert update["escalation"]["outcome"] == "EMERGENCY"
    # EMERGENCY always maps to CRITICAL regardless of the model's suggestion.
    assert update["escalation"]["ticket_priority"] == "CRITICAL"


async def test_escalate_fallback_uses_classifier_priority(monkeypatch, base_state):
    monkeypatch.setattr(llm, "structured_call", fake_structured({}))
    state = {**base_state, "classification": {"suggested_priority": "HIGH"}}
    update = await escalate(state)
    assert update["escalation"]["outcome"] == "NEEDS_TECHNICIAN"
    assert update["escalation"]["ticket_priority"] == "HIGH"


def test_routing_solved_assistant_skips_api_agent():
    state = {"channel": "assistant", "escalation": {"outcome": "SOLVED"}}
    assert route_after_escalate(state) == "summarize"


def test_routing_force_ticket_overrides_solved():
    state = {"channel": "assistant", "escalation": {"outcome": "SOLVED"}, "force_ticket": True}
    assert route_after_escalate(state) == "api_agent"


def test_routing_ticket_event_always_hits_api_agent():
    state = {"channel": "ticket_event", "escalation": {"outcome": "SOLVED"}}
    assert route_after_escalate(state) == "api_agent"


def test_routing_needs_technician_hits_api_agent():
    state = {"channel": "assistant", "escalation": {"outcome": "NEEDS_TECHNICIAN"}}
    assert route_after_escalate(state) == "api_agent"


async def test_structured_call_retries_once_then_none(monkeypatch):
    class Boom:
        calls = 0

        def with_structured_output(self, schema):
            return self

        async def ainvoke(self, prompt):
            Boom.calls += 1
            raise RuntimeError("model unavailable")

    monkeypatch.setattr(llm, "get_llm", lambda: Boom())
    result = await llm.structured_call(Troubleshooting, "prompt")
    assert result is None
    assert Boom.calls == 2
