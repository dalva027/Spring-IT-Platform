import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.adapters.queue import get_queue
from app.adapters.storage import get_storage
from app.security import AuthUser, verify_jwt

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze/tickets/{ticket_id}", status_code=status.HTTP_202_ACCEPTED)
async def analyze_ticket(
    ticket_id: int, response: Response, user: AuthUser = Depends(verify_jwt)
):
    """Enqueue a background analysis of an existing ticket (fired by the
    NewTicket form after creation). Returns 202 immediately."""
    request_id = uuid.uuid4()
    await get_storage().create_analysis(
        request_id,
        channel="ticket_event",
        issue_text="",  # filled in by the job once the ticket is fetched
        user_id=user.id,
        ticket_id=ticket_id,
    )
    await get_queue().enqueue(
        "analyze_ticket",
        {
            "requestId": str(request_id),
            "ticketId": ticket_id,
            "token": user.token,
            "user": {"id": user.id, "email": user.email, "role": user.role},
        },
    )
    response.headers["Location"] = f"/api/analyses/by-ticket/{ticket_id}"
    return {"requestId": str(request_id), "status": "QUEUED"}


@router.get("/analyses/by-ticket/{ticket_id}")
async def analysis_by_ticket(ticket_id: int, user: AuthUser = Depends(verify_jwt)):
    analysis = await get_storage().latest_analysis_for_ticket(ticket_id)
    if analysis is None:
        raise HTTPException(404, "No analysis for this ticket yet")
    return analysis
