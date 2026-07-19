"""Knowledge-base ingestion CLI (checksum-idempotent).

Usage: python -m app.rag.ingest [/knowledge-base]
"""

import asyncio
import hashlib
import logging
import sys
from pathlib import Path

from sqlalchemy import delete, select

from app.config import get_settings
from app.db.models import Chunk, Document
from app.db.session import session_factory
from app.rag.chunking import chunk_markdown, parse_front_matter
from app.rag.embeddings import get_embedder

logger = logging.getLogger(__name__)


async def ingest_file(path: Path) -> str:
    """Ingest one markdown file. Returns 'skipped', 'created' or 'updated'."""
    text = path.read_text(encoding="utf-8")
    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    parsed = parse_front_matter(text, fallback_title=path.stem)
    embedder = get_embedder()

    async with session_factory()() as session:
        result = await session.execute(select(Document).where(Document.path == path.name))
        existing = result.scalar_one_or_none()
        if (
            existing is not None
            and existing.checksum == checksum
            and existing.embedding_model == embedder.model
            and existing.embedding_dims == embedder.dims
        ):
            return "skipped"

        chunks = chunk_markdown(parsed.body)
        texts = [f"{parsed.title} — {c.heading}\n{c.content}" if c.heading else c.content
                 for c in chunks]
        embeddings = await embedder.embed_documents(texts)

        outcome = "created"
        if existing is not None:
            await session.execute(delete(Chunk).where(Chunk.document_id == existing.id))
            existing.title = parsed.title
            existing.category = parsed.category
            existing.checksum = checksum
            existing.embedding_model = embedder.model
            existing.embedding_dims = embedder.dims
            document = existing
            outcome = "updated"
        else:
            document = Document(
                path=path.name,
                title=parsed.title,
                category=parsed.category,
                checksum=checksum,
                embedding_model=embedder.model,
                embedding_dims=embedder.dims,
            )
            session.add(document)
            await session.flush()

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
            session.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk.content,
                    category=parsed.category,
                    heading=chunk.heading,
                    embedding=embedding,
                )
            )
        await session.commit()
        return outcome


async def ingest_directory(directory: str | Path | None = None) -> dict[str, int]:
    base = Path(directory or get_settings().knowledge_base_dir)
    counts = {"created": 0, "updated": 0, "skipped": 0, "failed": 0}
    for path in sorted(base.glob("*.md")):
        try:
            outcome = await ingest_file(path)
            counts[outcome] += 1
            logger.info("%s: %s", path.name, outcome)
        except Exception:
            counts["failed"] += 1
            logger.exception("failed to ingest %s", path.name)
    return counts


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    directory = sys.argv[1] if len(sys.argv) > 1 else None
    counts = asyncio.run(ingest_directory(directory))
    print(f"Ingest complete: {counts}")
    if counts["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
