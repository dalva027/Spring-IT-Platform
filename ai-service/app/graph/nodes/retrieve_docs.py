import logging
from typing import Any

from app.graph.state import HelpdeskState
from app.rag import retriever

logger = logging.getLogger(__name__)


async def retrieve_docs(state: HelpdeskState) -> dict[str, Any]:
    category = (state.get("classification") or {}).get("category")
    try:
        hits = await retriever.search_docs(state["issue_text"], category=category)
        return {"doc_hits": hits}
    except Exception as exc:
        logger.exception("doc retrieval failed")
        return {"doc_hits": [], "errors": [f"retrieve_docs: {exc}"]}
