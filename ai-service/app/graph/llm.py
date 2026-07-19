"""Gemini chat access. Every LLM node calls structured_call(); it enforces a
Pydantic schema, retries once with error feedback, and returns None on failure
so nodes can apply their deterministic fallbacks (the pipeline always
completes). Tests monkeypatch structured_call with a fake."""

import logging
from functools import lru_cache

from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_llm():
    from langchain_google_genai import ChatGoogleGenerativeAI

    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        temperature=0.1,
        google_api_key=settings.google_api_key or None,
    )


async def structured_call[T: BaseModel](schema: type[T], prompt: str) -> T | None:
    try:
        structured = get_llm().with_structured_output(schema)
    except Exception:
        logger.exception("LLM unavailable (missing GOOGLE_API_KEY?)")
        return None
    try:
        result = await structured.ainvoke(prompt)
    except Exception as first_error:
        logger.warning("structured call failed (%s), retrying once", first_error)
        retry_prompt = (
            f"{prompt}\n\nYour previous attempt failed with this error:\n{first_error}\n"
            "Respond again, strictly matching the required schema."
        )
        try:
            result = await structured.ainvoke(retry_prompt)
        except Exception:
            logger.exception("structured call failed after retry")
            return None
    if isinstance(result, schema):
        return result
    if isinstance(result, dict):
        try:
            return schema.model_validate(result)
        except Exception:
            return None
    return None
