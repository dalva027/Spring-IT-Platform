from typing import Any

from pydantic import BaseModel

from app.graph import llm, prompts
from app.graph.state import HelpdeskState


class Summaries(BaseModel):
    ticket_comment: str
    manager_summary: str
    resolution_notes: str


def _fallback(state: HelpdeskState) -> dict[str, str]:
    classification = state.get("classification") or {}
    steps = (state.get("troubleshooting") or {}).get("steps", [])
    outcome = (state.get("escalation") or {}).get("outcome", "NEEDS_TECHNICIAN")
    steps_text = "; ".join(steps) or "no steps generated"
    return {
        "ticket_comment": f"Automated analysis ({classification.get('category', '?')}, "
        f"{outcome}). Suggested steps: {steps_text}",
        "manager_summary": f"A {classification.get('category', '?')} issue was analyzed with "
        f"outcome {outcome}.",
        "resolution_notes": f"- Category: {classification.get('category', '?')}\n"
        f"- Outcome: {outcome}\n- Steps: {steps_text}",
    }


async def summarize(state: HelpdeskState) -> dict[str, Any]:
    result = await llm.structured_call(Summaries, prompts.summarize_prompt(dict(state)))
    if result is None:
        return {"summaries": _fallback(state), "errors": ["summarize: fell back to template"]}
    return {"summaries": result.model_dump()}
