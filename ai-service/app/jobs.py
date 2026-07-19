"""Queue job handlers. The 'analyze_ticket' job is the event flow behind the
NewTicket form: the frontend enqueues it fire-and-forget after creating a
ticket, carrying the employee's JWT."""

import logging
import uuid
from typing import Any

from app.adapters.queue import get_queue
from app.adapters.storage import get_storage
from app.adapters.ticket_client import TicketClient
from app.graph.runner import run_pipeline
from app.graph.state import HelpdeskState
from app.security import mint_service_token

logger = logging.getLogger(__name__)


async def handle_analyze_ticket(payload: dict[str, Any]) -> None:
    ticket_id = int(payload["ticketId"])
    user = payload.get("user") or {}
    request_id = uuid.UUID(payload["requestId"])

    # The service AGENT token can read any ticket.
    ticket = await TicketClient().get_ticket(mint_service_token(), ticket_id)
    issue_text = f"{ticket.get('title', '')}\n\n{ticket.get('description', '')}".strip()

    await get_storage().update_analysis(request_id, issue_text=issue_text)

    state: HelpdeskState = {
        "request_id": str(request_id),
        "channel": "ticket_event",
        "user": user,
        "user_token": payload.get("token", ""),
        "issue_text": issue_text,
        "existing_ticket_id": ticket_id,
        "errors": [],
    }
    await run_pipeline(state, request_id)


def register_handlers() -> None:
    get_queue().register_handler("analyze_ticket", handle_analyze_ticket)
