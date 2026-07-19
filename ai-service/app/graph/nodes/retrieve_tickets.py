import logging
from typing import Any

from app.graph.state import HelpdeskState
from app.rag import retriever

logger = logging.getLogger(__name__)


async def retrieve_tickets(state: HelpdeskState) -> dict[str, Any]:
    try:
        hits = await retriever.search_tickets(state["issue_text"])
        return {"ticket_hits": hits}
    except Exception as exc:
        logger.exception("ticket retrieval failed")
        return {"ticket_hits": [], "errors": [f"retrieve_tickets: {exc}"]}
