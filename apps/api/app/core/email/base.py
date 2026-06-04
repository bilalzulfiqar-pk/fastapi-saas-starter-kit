from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.email.schemas import EmailMessage


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> None:
        raise NotImplementedError

