"""Notifier seam: local impls are a Slack incoming webhook and SMTP (MailHog);
on AWS the same interface maps to SNS/SES."""

from abc import ABC, abstractmethod
from typing import Any


class Notifier(ABC):
    channel: str

    @abstractmethod
    async def send(self, subject: str, body: str, recipient: str = "") -> dict[str, Any]:
        """Returns a notification record: {channel, recipient, subject, body, status}."""
