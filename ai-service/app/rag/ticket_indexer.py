"""Embeds RESOLVED/CLOSED tickets so future requests can surface similar past
issues. Runs at startup (best effort) and via POST /api/admin/index-tickets."""

import logging

from sqlalchemy import select

from app.adapters.ticket_client import TicketClient
from app.db.models import TicketEmbedding, utcnow
from app.db.session import session_factory
from app.rag.embeddings import get_embedder
from app.security import mint_service_token

logger = logging.getLogger(__name__)


async def index_resolved_tickets(client: TicketClient | None = None) -> dict[str, int]:
    client = client or TicketClient()
    embedder = get_embedder()
    counts = {"indexed": 0, "skipped": 0}

    for status in ("RESOLVED", "CLOSED"):
        page = 0
        while True:
            token = mint_service_token()  # re-mint per page; 5-minute TTL
            result = await client.search_tickets(token, status=status, page=page, size=50)
            tickets = result.get("content", [])
            if not tickets:
                break
            for ticket in tickets:
                if await _index_one(ticket, embedder):
                    counts["indexed"] += 1
                else:
                    counts["skipped"] += 1
            total_pages = result.get("page", {}).get("totalPages", 0)
            page += 1
            if page >= total_pages:
                break
    return counts


async def _index_one(ticket: dict, embedder) -> bool:
    ticket_id = ticket["id"]
    snippet = (ticket.get("description") or "")[:1000]
    async with session_factory()() as session:
        result = await session.execute(
            select(TicketEmbedding).where(TicketEmbedding.ticket_id == ticket_id)
        )
        existing = result.scalar_one_or_none()
        if (
            existing is not None
            and existing.status == ticket.get("status")
            and existing.embedding_model == embedder.model
        ):
            return False

        embedding = await embedder.embed_documents([f"{ticket.get('title', '')}\n{snippet}"])
        if existing is not None:
            existing.title = (ticket.get("title") or "")[:255]
            existing.snippet = snippet
            existing.status = ticket.get("status", "")
            existing.embedding = embedding[0]
            existing.embedding_model = embedder.model
            existing.embedding_dims = embedder.dims
            existing.indexed_at = utcnow()
        else:
            session.add(
                TicketEmbedding(
                    ticket_id=ticket_id,
                    title=(ticket.get("title") or "")[:255],
                    snippet=snippet,
                    status=ticket.get("status", ""),
                    embedding=embedding[0],
                    embedding_model=embedder.model,
                    embedding_dims=embedder.dims,
                )
            )
        await session.commit()
        return True
