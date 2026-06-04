from __future__ import annotations

import logging

from app.core.email.base import EmailProvider
from app.core.email.schemas import EmailMessage

logger = logging.getLogger(__name__)


class ConsoleEmailProvider(EmailProvider):
    async def send(self, message: EmailMessage) -> None:
        logger.info("Console email delivery | to=%s subject=%s\n%s", message.to, message.subject, message.text_body)

