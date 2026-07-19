import logging
from typing import Any

import httpx

from app.adapters.notify.base import Notifier
from app.config import get_settings

logger = logging.getLogger(__name__)


class SlackNotifier(Notifier):
    channel = "slack"

    def __init__(self, webhook_url: str | None = None):
        if webhook_url is None:
            webhook_url = get_settings().slack_webhook_url
        self.webhook_url = webhook_url

    async def send(self, subject: str, body: str, recipient: str = "") -> dict[str, Any]:
        record = {
            "channel": self.channel,
            "recipient": recipient or "#it-helpdesk",
            "subject": subject,
            "body": body,
        }
        if not self.webhook_url:
            return {**record, "status": "SKIPPED"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url, json={"text": f"*{subject}*\n{body}"}
                )
            response.raise_for_status()
            return {**record, "status": "SENT"}
        except Exception:
            logger.exception("Slack notification failed")
            return {**record, "status": "FAILED"}
