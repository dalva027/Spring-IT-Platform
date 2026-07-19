"""The agent that acts on the real system: creates the ticket (employee token),
posts the AI comment (service token), opens mock external issues and sends
notifications. Behavior depends on the channel:

- assistant: create ticket → AI comment → external issue for NETWORKING/SECURITY
  or EMERGENCY → Slack + email.
- ticket_event: never create or re-prioritize a ticket; only comment on the
  existing one and notify on EMERGENCY.
"""

import logging
from typing import Any

from app.adapters.external.mock import MockExternalTracker
from app.adapters.notify.email import EmailNotifier
from app.adapters.notify.slack import SlackNotifier
from app.adapters.storage import get_storage
from app.adapters.ticket_client import TicketClient
from app.graph.state import HelpdeskState
from app.security import mint_service_token

logger = logging.getLogger(__name__)

_PROVIDER_BY_CATEGORY = {"NETWORKING": "jira", "SECURITY": "servicenow"}


# Factory seams so unit tests can monkeypatch with fakes.
def get_ticket_client() -> TicketClient:
    return TicketClient()


def get_notifiers() -> list:
    return [SlackNotifier(), EmailNotifier()]


def get_tracker(provider: str) -> MockExternalTracker:
    return MockExternalTracker(provider)


def _ticket_title(issue_text: str) -> str:
    first_line = issue_text.strip().splitlines()[0]
    return (first_line[:197] + "…") if len(first_line) > 198 else first_line


def format_ai_comment(state: HelpdeskState) -> str:
    classification = state.get("classification") or {}
    troubleshooting = state.get("troubleshooting") or {}
    escalation = state.get("escalation") or {}
    steps = "\n".join(f"{i}. {step}" for i, step in enumerate(troubleshooting.get("steps", []), 1))
    doc_titles = {hit["title"] for hit in (state.get("doc_hits") or [])}
    sources = ", ".join(sorted(doc_titles)) or "none"
    return (
        "AI analysis\n"
        f"Category: {classification.get('category', '?')} "
        f"(confidence {classification.get('confidence', 0):.0%})\n"
        f"Outcome: {escalation.get('outcome', '?')} — {escalation.get('assignment_hint', '')}\n\n"
        f"Suggested troubleshooting steps:\n{steps or '(none)'}\n\n"
        f"Knowledge-base sources: {sources}"
    )


async def api_agent(state: HelpdeskState) -> dict[str, Any]:
    channel = state.get("channel", "assistant")
    classification = state.get("classification") or {}
    escalation = state.get("escalation") or {}
    outcome = escalation.get("outcome", "NEEDS_TECHNICIAN")
    errors: list[str] = []
    updates: dict[str, Any] = {}

    client = get_ticket_client()
    service_token = mint_service_token()

    # 1. Ticket: create for the assistant channel (employee token, requesterId =
    #    the employee's sub); never create or re-prioritize for ticket_event.
    ticket_id = state.get("existing_ticket_id")
    if channel == "assistant":
        priority = (
            "CRITICAL" if outcome == "EMERGENCY"
            else classification.get("suggested_priority", "MEDIUM")
        )
        try:
            ticket = await client.create_ticket(
                state["user_token"],
                title=_ticket_title(state["issue_text"]),
                description=state["issue_text"],
                priority=priority,
            )
            ticket_id = ticket["id"]
        except Exception as exc:
            logger.exception("ticket creation failed")
            errors.append(f"api_agent: ticket creation failed: {exc}")
    updates["ticket_id"] = ticket_id

    # 2. AI comment, authored by the seeded AI Assistant (service AGENT token).
    if ticket_id is not None:
        try:
            await client.add_comment(service_token, ticket_id, format_ai_comment(state))
        except Exception as exc:
            logger.exception("AI comment failed")
            errors.append(f"api_agent: AI comment failed: {exc}")

    # 3. Mock external issue for NETWORKING/SECURITY or any EMERGENCY.
    external_issues: list[dict[str, Any]] = []
    category = classification.get("category", "")
    if channel == "assistant" and (category in _PROVIDER_BY_CATEGORY or outcome == "EMERGENCY"):
        provider = _PROVIDER_BY_CATEGORY.get(category, "freshdesk")
        try:
            issue = await get_tracker(provider).create_issue(
                summary=_ticket_title(state["issue_text"]),
                description=state["issue_text"],
                request_id=state.get("request_id"),
                ticket_id=ticket_id,
            )
            external_issues.append(issue)
        except Exception as exc:
            logger.exception("external issue creation failed")
            errors.append(f"api_agent: external issue failed: {exc}")
    updates["external_issues"] = external_issues

    # 4. Notifications: always for assistant runs, EMERGENCY-only for ticket events.
    notifications: list[dict[str, Any]] = []
    if channel == "assistant" or outcome == "EMERGENCY":
        subject = (
            f"[{'EMERGENCY' if outcome == 'EMERGENCY' else category or 'HELPDESK'}] "
            f"Ticket #{ticket_id}: {_ticket_title(state['issue_text'])}"
        )
        body = (
            f"Outcome: {outcome}\n"
            f"Priority: {escalation.get('ticket_priority', '?')}\n"
            f"Assignment hint: {escalation.get('assignment_hint', '-')}\n"
            f"Requested by user {state.get('user', {}).get('email', '?')}"
        )
        for notifier in get_notifiers():
            try:
                record = await notifier.send(subject, body)
            except Exception as exc:  # notifier bugs must not break the pipeline
                logger.exception("notifier %s failed", getattr(notifier, "channel", "?"))
                record = {"channel": getattr(notifier, "channel", "?"), "status": "FAILED"}
                errors.append(f"api_agent: notification failed: {exc}")
            record["requestId"] = state.get("request_id")
            record["ticketId"] = ticket_id
            notifications.append(record)
            try:
                await get_storage().record_notification(record)
            except Exception:
                logger.debug("could not persist notification record", exc_info=True)
    updates["notifications"] = notifications

    if errors:
        updates["errors"] = errors
    return updates
