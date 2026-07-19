"""Gemini embeddings pinned to a fixed dimensionality so vectors in pgvector
stay comparable. Model + dims are stored per document; the retriever refuses
mixed-dim data."""

import asyncio
from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import get_settings


class Embedder:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.gemini_embedding_model
        self.dims = settings.embedding_dims
        self._client = GoogleGenerativeAIEmbeddings(
            model=self.model, google_api_key=settings.google_api_key or None
        )

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(
            self._client.embed_documents, texts, output_dimensionality=self.dims
        )

    async def embed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(
            self._client.embed_query, text, output_dimensionality=self.dims
        )


@lru_cache
def get_embedder() -> Embedder:
    return Embedder()
