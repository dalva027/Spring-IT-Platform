import uuid
from typing import Any

from sqlalchemy import func, select

from app.adapters.storage.base import StorageAdapter
from app.db.models import AgentEvent, Analysis, ExternalIssue, Notification
from app.db.session import session_factory


def _analysis_to_dict(analysis: Analysis) -> dict[str, Any]:
    return {
        "requestId": str(analysis.request_id),
        "channel": analysis.channel,
        "status": analysis.status,
        "issueText": analysis.issue_text,
        "userId": analysis.user_id,
        "ticketId": analysis.ticket_id,
        "classification": analysis.classification,
        "docHits": analysis.doc_hits,
        "ticketHits": analysis.ticket_hits,
        "troubleshooting": analysis.troubleshooting,
        "escalation": analysis.escalation,
        "externalIssues": analysis.external_issues,
        "notifications": analysis.notifications,
        "summaries": analysis.summaries,
        "errors": analysis.errors,
        "createdAt": analysis.created_at.isoformat() if analysis.created_at else None,
        "updatedAt": analysis.updated_at.isoformat() if analysis.updated_at else None,
    }


class PostgresStorage(StorageAdapter):
    async def create_analysis(
        self, request_id: uuid.UUID, channel: str, issue_text: str, user_id: int,
        ticket_id: int | None = None,
    ) -> None:
        async with session_factory()() as session:
            session.add(
                Analysis(
                    request_id=request_id,
                    channel=channel,
                    issue_text=issue_text,
                    user_id=user_id,
                    ticket_id=ticket_id,
                    status="RUNNING",
                )
            )
            await session.commit()

    async def update_analysis(self, request_id: uuid.UUID, **fields: Any) -> None:
        async with session_factory()() as session:
            analysis = await session.get(Analysis, request_id)
            if analysis is None:
                return
            for key, value in fields.items():
                setattr(analysis, key, value)
            await session.commit()

    async def get_analysis(self, request_id: uuid.UUID) -> dict[str, Any] | None:
        async with session_factory()() as session:
            analysis = await session.get(Analysis, request_id)
            return _analysis_to_dict(analysis) if analysis else None

    async def latest_analysis_for_ticket(self, ticket_id: int) -> dict[str, Any] | None:
        async with session_factory()() as session:
            result = await session.execute(
                select(Analysis)
                .where(Analysis.ticket_id == ticket_id)
                .order_by(Analysis.created_at.desc())
                .limit(1)
            )
            analysis = result.scalar_one_or_none()
            return _analysis_to_dict(analysis) if analysis else None

    async def append_event(
        self, request_id: uuid.UUID, event_type: str, node: str, payload: dict[str, Any] | None
    ) -> int:
        async with session_factory()() as session:
            result = await session.execute(
                select(func.coalesce(func.max(AgentEvent.seq), 0)).where(
                    AgentEvent.request_id == request_id
                )
            )
            seq = int(result.scalar_one()) + 1
            session.add(
                AgentEvent(
                    request_id=request_id,
                    seq=seq,
                    event_type=event_type,
                    node=node,
                    payload=payload,
                )
            )
            await session.commit()
            return seq

    async def list_events(self, request_id: uuid.UUID) -> list[dict[str, Any]]:
        async with session_factory()() as session:
            result = await session.execute(
                select(AgentEvent)
                .where(AgentEvent.request_id == request_id)
                .order_by(AgentEvent.seq)
            )
            return [
                {
                    "seq": event.seq,
                    "eventType": event.event_type,
                    "node": event.node,
                    "payload": event.payload,
                    "createdAt": event.created_at.isoformat() if event.created_at else None,
                }
                for event in result.scalars()
            ]

    async def record_external_issue(self, issue: dict[str, Any]) -> None:
        async with session_factory()() as session:
            session.add(
                ExternalIssue(
                    provider=issue["provider"],
                    external_key=issue["key"],
                    request_id=uuid.UUID(issue["requestId"]) if issue.get("requestId") else None,
                    ticket_id=issue.get("ticketId"),
                    summary=issue.get("summary", "")[:512],
                    url=issue.get("url", "")[:512],
                    payload=issue.get("payload"),
                )
            )
            await session.commit()

    async def record_notification(self, notification: dict[str, Any]) -> None:
        async with session_factory()() as session:
            session.add(
                Notification(
                    channel=notification["channel"],
                    recipient=notification.get("recipient", "")[:255],
                    subject=notification.get("subject", "")[:512],
                    body=notification.get("body", ""),
                    status=notification["status"],
                    request_id=(
                        uuid.UUID(notification["requestId"])
                        if notification.get("requestId")
                        else None
                    ),
                    ticket_id=notification.get("ticketId"),
                )
            )
            await session.commit()
