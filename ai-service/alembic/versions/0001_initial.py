"""Initial ai_db schema: RAG tables, analyses, external issues, notifications, events, jobs.

Revision ID: 0001
Revises:
Create Date: 2026-07-18
"""

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

DIMS = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("path", sa.String(512), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("embedding_model", sa.String(128), nullable=False),
        sa.Column("embedding_dims", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "document_id",
            sa.BigInteger,
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("heading", sa.String(255), nullable=False, server_default=""),
        sa.Column("embedding", Vector(DIMS), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_chunks_embedding_hnsw",
        "chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    op.create_table(
        "ticket_embeddings",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("ticket_id", sa.BigInteger, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("snippet", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("embedding", Vector(DIMS), nullable=False),
        sa.Column("embedding_model", sa.String(128), nullable=False),
        sa.Column("embedding_dims", sa.Integer, nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("ticket_id", name="uq_ticket_embeddings_ticket_id"),
    )
    op.create_index(
        "ix_ticket_embeddings_embedding_hnsw",
        "ticket_embeddings",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    op.create_table(
        "analyses",
        sa.Column("request_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("issue_text", sa.Text, nullable=False),
        sa.Column("user_id", sa.BigInteger, nullable=False),
        sa.Column("ticket_id", sa.BigInteger, nullable=True),
        sa.Column("classification", JSONB, nullable=True),
        sa.Column("doc_hits", JSONB, nullable=True),
        sa.Column("ticket_hits", JSONB, nullable=True),
        sa.Column("troubleshooting", JSONB, nullable=True),
        sa.Column("escalation", JSONB, nullable=True),
        sa.Column("external_issues", JSONB, nullable=True),
        sa.Column("notifications", JSONB, nullable=True),
        sa.Column("summaries", JSONB, nullable=True),
        sa.Column("errors", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analyses_ticket_id", "analyses", ["ticket_id"])

    op.create_table(
        "external_issues",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("external_key", sa.String(64), nullable=False),
        sa.Column("request_id", UUID(as_uuid=True), nullable=True),
        sa.Column("ticket_id", sa.BigInteger, nullable=True),
        sa.Column("summary", sa.String(512), nullable=False),
        sa.Column("url", sa.String(512), nullable=False),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_external_issues_ticket_id", "external_issues", ["ticket_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("recipient", sa.String(255), nullable=False, server_default=""),
        sa.Column("subject", sa.String(512), nullable=False, server_default=""),
        sa.Column("body", sa.Text, nullable=False, server_default=""),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("request_id", UUID(as_uuid=True), nullable=True),
        sa.Column("ticket_id", sa.BigInteger, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "agent_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("request_id", UUID(as_uuid=True), nullable=False),
        sa.Column("seq", sa.Integer, nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("node", sa.String(64), nullable=False, server_default=""),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agent_events_request_id", "agent_events", ["request_id", "seq"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text, nullable=False, server_default=""),
        sa.Column("run_after", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_jobs_status_run_after", "jobs", ["status", "run_after"])


def downgrade() -> None:
    for table in (
        "jobs",
        "agent_events",
        "notifications",
        "external_issues",
        "analyses",
        "ticket_embeddings",
        "chunks",
        "documents",
    ):
        op.drop_table(table)
