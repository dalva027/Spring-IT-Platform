from typing import Any, Literal

from pydantic import BaseModel

from app.graph import llm, prompts
from app.graph.state import HelpdeskState

Outcome = Literal["SOLVED", "NEEDS_TECHNICIAN", "EMERGENCY"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class Escalation(BaseModel):
    outcome: Outcome
    ticket_priority: Priority
    assignment_hint: str


def _normalize(escalation: dict[str, Any]) -> dict[str, Any]:
    # Deterministic invariant regardless of what the model said.
    if escalation["outcome"] == "EMERGENCY":
        escalation["ticket_priority"] = "CRITICAL"
    return escalation


async def escalate(state: HelpdeskState) -> dict[str, Any]:
    prompt = prompts.escalate_prompt(
        state["issue_text"],
        state.get("classification") or {},
        state.get("troubleshooting") or {},
    )
    result = await llm.structured_call(Escalation, prompt)
    if result is None:
        suggested = (state.get("classification") or {}).get("suggested_priority", "MEDIUM")
        return {
            "escalation": _normalize(
                {
                    "outcome": "NEEDS_TECHNICIAN",
                    "ticket_priority": suggested,
                    "assignment_hint": "General IT support",
                }
            ),
            "errors": ["escalate: fell back to NEEDS_TECHNICIAN"],
        }
    return {"escalation": _normalize(result.model_dump())}
