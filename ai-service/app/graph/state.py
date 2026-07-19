import operator
from typing import Annotated, Any, TypedDict


class HelpdeskState(TypedDict, total=False):
    request_id: str  # uuid; doubles as the checkpointer thread_id
    channel: str  # "assistant" | "ticket_event"
    user: dict[str, Any]  # {id, email, role}
    user_token: str  # employee JWT, passed through for ticket creation
    issue_text: str
    existing_ticket_id: int | None
    force_ticket: bool  # set when the UI resumes a SOLVED run via "Create ticket anyway"

    classification: dict[str, Any]  # {category, suggested_priority, confidence, rationale}
    doc_hits: list[dict[str, Any]]
    ticket_hits: list[dict[str, Any]]
    troubleshooting: dict[str, Any]  # {steps, self_serviceable, confidence}
    escalation: dict[str, Any]  # {outcome, ticket_priority, assignment_hint}
    ticket_id: int | None
    external_issues: list[dict[str, Any]]
    notifications: list[dict[str, Any]]
    summaries: dict[str, Any]  # {ticket_comment, manager_summary, resolution_notes}

    errors: Annotated[list[str], operator.add]
