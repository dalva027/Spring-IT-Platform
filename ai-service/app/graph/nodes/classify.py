from typing import Any, Literal

from pydantic import BaseModel, Field

from app.graph import llm, prompts
from app.graph.state import HelpdeskState

Category = Literal["IT", "HR", "FINANCE", "NETWORKING", "SECURITY"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

FALLBACK = {
    "category": "IT",
    "suggested_priority": "MEDIUM",
    "confidence": 0.0,
    "rationale": "Fallback: the language model was unavailable or returned invalid output.",
}


class Classification(BaseModel):
    category: Category
    suggested_priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str


async def classify(state: HelpdeskState) -> dict[str, Any]:
    result = await llm.structured_call(Classification, prompts.classify_prompt(state["issue_text"]))
    if result is None:
        return {"classification": dict(FALLBACK), "errors": ["classify: fell back to IT/MEDIUM"]}
    return {"classification": result.model_dump()}
