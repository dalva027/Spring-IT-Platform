from fastapi import APIRouter, Depends

from app.rag.ingest import ingest_directory
from app.rag.ticket_indexer import index_resolved_tickets
from app.security import AuthUser, require_agent

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest")
async def ingest(user: AuthUser = Depends(require_agent)):
    """Re-ingest the knowledge base (checksum-idempotent)."""
    return await ingest_directory()


@router.post("/index-tickets")
async def index_tickets(user: AuthUser = Depends(require_agent)):
    """Embed RESOLVED/CLOSED tickets for similar-ticket retrieval."""
    return await index_resolved_tickets()
