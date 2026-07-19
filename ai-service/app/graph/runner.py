"""Runs the pipeline and translates LangGraph execution into a stream of
progress events (node_start / node_end / result / error). Every event is also
persisted to agent_events (SSE recovery / replay) and node outputs are folded
into the analyses row as they land."""

import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

from app.adapters.storage import get_storage
from app.graph.builder import NODE_ORDER, get_graph
from app.graph.state import HelpdeskState

logger = logging.getLogger(__name__)

NODE_LABELS = {
    "classify": "Classifying the issue",
    "retrieve_docs": "Searching company docs",
    "retrieve_tickets": "Searching past tickets",
    "troubleshoot": "Drafting troubleshooting steps",
    "escalate": "Deciding on escalation",
    "api_agent": "Acting on the ticket system",
    "summarize": "Writing summaries",
}

_STATE_TO_ANALYSIS = {
    "classification": "classification",
    "doc_hits": "doc_hits",
    "ticket_hits": "ticket_hits",
    "troubleshooting": "troubleshooting",
    "escalation": "escalation",
    "ticket_id": "ticket_id",
    "external_issues": "external_issues",
    "notifications": "notifications",
    "summaries": "summaries",
}

_NODE_SET = set(NODE_ORDER)


async def _persist_node_output(request_id: uuid.UUID, output: dict[str, Any]) -> None:
    fields = {
        column: output[key] for key, column in _STATE_TO_ANALYSIS.items() if key in output
    }
    if output.get("errors"):
        analysis = await get_storage().get_analysis(request_id)
        existing = (analysis or {}).get("errors") or []
        fields["errors"] = existing + output["errors"]
    if fields:
        await get_storage().update_analysis(request_id, **fields)


def _public_payload(node: str, output: dict[str, Any]) -> dict[str, Any]:
    """What the SSE stream exposes for a finished node (trimmed state delta)."""
    payload = {
        key: value for key, value in output.items() if key in _STATE_TO_ANALYSIS or key == "errors"
    }
    payload["label"] = NODE_LABELS.get(node, node)
    return payload


async def stream_pipeline(
    initial_state: HelpdeskState | None, request_id: uuid.UUID
) -> AsyncIterator[dict[str, Any]]:
    """Yields {type, node, payload} events. Pass initial_state=None to resume
    from the existing checkpoint (create-ticket-anyway flow)."""
    graph = get_graph()
    config = {"configurable": {"thread_id": str(request_id)}}
    storage = get_storage()
    failed = False
    started: set[str] = set()
    ended: set[str] = set()

    try:
        async for event in graph.astream_events(initial_state, config, version="v2"):
            kind = event.get("event")
            node = event.get("name", "")
            if node not in _NODE_SET:
                continue
            # The node wrapper and its inner callable share the node name —
            # dedup so each node yields exactly one start and one end.
            if kind == "on_chain_start" and node not in started:
                started.add(node)
                payload = {"label": NODE_LABELS.get(node, node)}
                await storage.append_event(request_id, "node_start", node, payload)
                yield {"type": "node_start", "node": node, "payload": payload}
            elif kind == "on_chain_end" and node not in ended:
                ended.add(node)
                output = event.get("data", {}).get("output")
                output = output if isinstance(output, dict) else {}
                await _persist_node_output(request_id, output)
                payload = _public_payload(node, output)
                await storage.append_event(request_id, "node_end", node, payload)
                yield {"type": "node_end", "node": node, "payload": payload}
    except Exception as exc:
        logger.exception("pipeline run %s failed", request_id)
        failed = True
        await storage.update_analysis(request_id, status="FAILED")
        payload = {"message": str(exc)[:500]}
        await storage.append_event(request_id, "error", "", payload)
        yield {"type": "error", "node": "", "payload": payload}

    if not failed:
        await storage.update_analysis(request_id, status="COMPLETED")
        analysis = await storage.get_analysis(request_id)
        await storage.append_event(request_id, "result", "", analysis)
        yield {"type": "result", "node": "", "payload": analysis}


async def run_pipeline(
    initial_state: HelpdeskState, request_id: uuid.UUID
) -> dict[str, Any] | None:
    """Non-streaming execution (queue jobs). Consumes the same event stream so
    agent_events/analyses are populated identically."""
    result: dict[str, Any] | None = None
    async for event in stream_pipeline(initial_state, request_id):
        if event["type"] == "result":
            result = event["payload"]
    return result


async def resume_with_ticket(request_id: uuid.UUID) -> dict[str, Any] | None:
    """Create-ticket-anyway: fork the finished checkpoint as-if escalate just
    ran with force_ticket=True, then continue (routes through api_agent)."""
    graph = get_graph()
    config = {"configurable": {"thread_id": str(request_id)}}
    await graph.aupdate_state(config, {"force_ticket": True}, as_node="escalate")
    result: dict[str, Any] | None = None
    async for event in stream_pipeline(None, request_id):
        if event["type"] == "result":
            result = event["payload"]
    return result
