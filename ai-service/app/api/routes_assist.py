import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.adapters.storage import get_storage
from app.api.sse import SSE_HEADERS, format_sse, with_heartbeat
from app.graph import runner
from app.graph.state import HelpdeskState
from app.security import AuthUser, verify_jwt

router = APIRouter(prefix="/api/assist", tags=["assist"])


class AssistRequest(BaseModel):
    issue_text: str = Field(min_length=5, max_length=10000)


@router.post("/stream")
async def assist_stream(body: AssistRequest, user: AuthUser = Depends(verify_jwt)):
    """Run the agent pipeline for a natural-language issue, streaming progress
    as SSE frames (node_start / node_end / result / error)."""
    request_id = uuid.uuid4()
    await get_storage().create_analysis(
        request_id, channel="assistant", issue_text=body.issue_text, user_id=user.id
    )

    state: HelpdeskState = {
        "request_id": str(request_id),
        "channel": "assistant",
        "user": {"id": user.id, "email": user.email, "role": user.role},
        "user_token": user.token,
        "issue_text": body.issue_text,
        "errors": [],
    }

    async def frames() -> AsyncIterator[str]:
        yield format_sse("started", {"requestId": str(request_id)})
        async for event in runner.stream_pipeline(state, request_id):
            yield format_sse(event["type"], {"node": event["node"], **(event["payload"] or {})})

    return StreamingResponse(
        with_heartbeat(frames()), media_type="text/event-stream", headers=SSE_HEADERS
    )


@router.post("/{request_id}/create-ticket")
async def create_ticket_anyway(request_id: uuid.UUID, user: AuthUser = Depends(verify_jwt)):
    """Resume a SOLVED assistant run through api_agent ('Create ticket anyway')."""
    analysis = await get_storage().get_analysis(request_id)
    if analysis is None:
        raise HTTPException(404, "Unknown request id")
    if analysis["userId"] != user.id and not user.is_agent:
        raise HTTPException(403, "Not your assistant session")
    if analysis.get("ticketId"):
        return analysis  # already has a ticket; idempotent
    result = await runner.resume_with_ticket(request_id)
    if result is None:
        raise HTTPException(409, "Could not resume this analysis")
    return result


@router.get("/{request_id}/events")
async def list_events(request_id: uuid.UUID, user: AuthUser = Depends(verify_jwt)):
    """Replay persisted agent events (UI state recovery after a refresh)."""
    analysis = await get_storage().get_analysis(request_id)
    if analysis is None:
        raise HTTPException(404, "Unknown request id")
    if analysis["userId"] != user.id and not user.is_agent:
        raise HTTPException(403, "Not your assistant session")
    return {"analysis": analysis, "events": await get_storage().list_events(request_id)}
