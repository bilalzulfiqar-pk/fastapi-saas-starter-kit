from __future__ import annotations

from pydantic import BaseModel, EmailStr


class EmailMessage(BaseModel):
    to: EmailStr
    subject: str
    text_body: str
    html_body: str | None = None

