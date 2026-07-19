from typing import Any

from pydantic import BaseModel, Field

from app.graph import llm, prompts
from app.graph.state import HelpdeskState

FALLBACK_STEPS = [
    "Restart the affected application or device and try to reproduce the problem.",
    "Note any exact error messages and when the problem started.",
    "A support technician will follow up on your ticket with next steps.",
]


class Troubleshooting(BaseModel):
    steps: list[str] = Field(min_length=1, max_length=10)
    self_serviceable: bool
    confidence: float = Field(ge=0.0, le=1.0)


async def troubleshoot(state: HelpdeskState) -> dict[str, Any]:
    prompt = prompts.troubleshoot_prompt(
        state["issue_text"],
        state.get("classification") or {},
        state.get("doc_hits") or [],
        state.get("ticket_hits") or [],
    )
    result = await llm.structured_call(Troubleshooting, prompt)
    if result is None:
        return {
            "troubleshooting": {
                "steps": list(FALLBACK_STEPS),
                "self_serviceable": False,
                "confidence": 0.0,
            },
            "errors": ["troubleshoot: fell back to generic steps"],
        }
    return {"troubleshooting": result.model_dump()}
