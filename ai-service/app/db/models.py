import uuid
from datetime import UTC, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import get_settings

EMBEDDING_DIMS = get_settings().embedding_dims


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Document(Base):
    """One ingested knowledge-base markdown file."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(512), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(32))
    checksum: Mapped[str] = mapped_column(String(64))
    embedding_model: Mapped[str] = mapped_column(String(128))
    embedding_dims: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(32))
    heading: Mapped[str] = mapped_column(String(255), default="")
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMS))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TicketEmbedding(Base):
    """Embedded RESOLVED/CLOSED tickets for similar-issue retrieval."""

    __tablename__ = "ticket_embeddings"
    __table_args__ = (
        UniqueConstraint("ticket_id", name="uq_ticket_embeddings_ticket_id"),
        Index(
            "ix_ticket_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(255))
    snippet: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32))
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMS))
    embedding_model: Mapped[str] = mapped_column(String(128))
    embedding_dims: Mapped[int] = mapped_column(Integer)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Analysis(Base):
    """One pipeline run (assistant conversation or ticket_event analysis)."""

    __tablename__ = "analyses"
    __table_args__ = (Index("ix_analyses_ticket_id", "ticket_id"),)

    request_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    channel: Mapped[str] = mapped_column(String(32))  # assistant | ticket_event
    status: Mapped[str] = mapped_column(String(32), default="RUNNING")  # RUNNING|COMPLETED|FAILED
    issue_text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(BigInteger)
    ticket_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    classification: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    doc_hits: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    ticket_hits: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    troubleshooting: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    escalation: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    external_issues: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    notifications: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    summaries: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    errors: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class ExternalIssue(Base):
    """Persisted fake Jira/ServiceNow/Freshdesk issues created by the mock adapters."""

    __tablename__ = "external_issues"
    __table_args__ = (Index("ix_external_issues_ticket_id", "ticket_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(32))
    external_key: Mapped[str] = mapped_column(String(64))
    request_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    ticket_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    summary: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(512))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    channel: Mapped[str] = mapped_column(String(32))  # slack | email
    recipient: Mapped[str] = mapped_column(String(255), default="")
    subject: Mapped[str] = mapped_column(String(512), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32))  # SENT | SKIPPED | FAILED
    request_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    ticket_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AgentEvent(Base):
    """Per-node progress events; drives SSE and lets the UI replay after refresh."""

    __tablename__ = "agent_events"
    __table_args__ = (Index("ix_agent_events_request_id", "request_id", "seq"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[uuid.UUID] = mapped_column()
    seq: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(32))  # node_start|node_end|result|error
    node: Mapped[str] = mapped_column(String(64), default="")
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Job(Base):
    """DB-backed queue (the SQS seam): the in-process worker polls this table."""

    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_status_run_after", "status", "run_after"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    # PENDING | RUNNING | DONE | FAILED
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(Text, default="")
    run_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
