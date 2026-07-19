"""Cosine top-k retrieval over knowledge-base chunks and past-ticket embeddings."""

from typing import Any

from sqlalchemy import select

from app.config import get_settings
from app.db.models import Chunk, Document, TicketEmbedding
from app.db.session import session_factory
from app.rag.embeddings import get_embedder


async def search_docs(
    query: str, category: str | None = None, top_k: int | None = None
) -> list[dict[str, Any]]:
    settings = get_settings()
    top_k = top_k or settings.retrieval_top_k
    embedding = await get_embedder().embed_query(query)

    async with session_factory()() as session:
        distance = Chunk.embedding.cosine_distance(embedding)
        stmt = (
            select(Chunk, Document, distance.label("distance"))
            .join(Document, Chunk.document_id == Document.id)
            # Refuse mixed-dimensionality data: only match rows embedded with
            # the currently configured model+dims.
            .where(
                Document.embedding_model == get_embedder().model,
                Document.embedding_dims == get_embedder().dims,
            )
            .order_by(distance)
            .limit(top_k)
        )
        if category:
            stmt = stmt.where(Chunk.category == category.upper())
        result = await session.execute(stmt)
        hits = [
            {
                "title": document.title,
                "path": document.path,
                "category": chunk.category,
                "heading": chunk.heading,
                "snippet": chunk.content[:800],
                "score": round(1.0 - float(dist), 4),
            }
            for chunk, document, dist in result.all()
        ]

    # If the category filter starved the results, retry unfiltered.
    if category and not hits:
        return await search_docs(query, category=None, top_k=top_k)
    return hits


async def search_tickets(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    settings = get_settings()
    top_k = top_k or settings.retrieval_top_k
    embedding = await get_embedder().embed_query(query)

    async with session_factory()() as session:
        distance = TicketEmbedding.embedding.cosine_distance(embedding)
        stmt = (
            select(TicketEmbedding, distance.label("distance"))
            .where(
                TicketEmbedding.embedding_model == get_embedder().model,
                TicketEmbedding.embedding_dims == get_embedder().dims,
            )
            .order_by(distance)
            .limit(top_k)
        )
        result = await session.execute(stmt)
        return [
            {
                "ticketId": row.ticket_id,
                "title": row.title,
                "snippet": row.snippet[:500],
                "status": row.status,
                "score": round(1.0 - float(dist), 4),
            }
            for row, dist in result.all()
        ]
