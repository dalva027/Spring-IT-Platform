import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import Any

from app.adapters.notify.base import Notifier
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    channel = "email"

    def __init__(self, host: str | None = None, port: int | None = None):
        settings = get_settings()
        self.host = host or settings.smtp_host
        self.port = port or settings.smtp_port
        self.sender = settings.smtp_from

    def _send_sync(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            smtp.send_message(message)

    async def send(self, subject: str, body: str, recipient: str = "") -> dict[str, Any]:
        recipient = recipient or "it-helpdesk@helpdesk.local"
        record = {"channel": self.channel, "recipient": recipient, "subject": subject, "body": body}
        try:
            await asyncio.to_thread(self._send_sync, recipient, subject, body)
            return {**record, "status": "SENT"}
        except Exception:
            logger.exception("email notification failed")
            return {**record, "status": "FAILED"}
