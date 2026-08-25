from datetime import date
from typing import ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator



class SearchQuery(BaseModel):
    name: str
    sender: str | None
    receiver: str | None
    subject_contains: list[str] = Field(default_factory=list)
    body_contains: list[str]= Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    before: date | None = None
    after: date | None=None
    is_read: bool | None = None
    is_starred: bool | None = None
    has_attachments: bool | None = None

    _GMAIL_LIST_OPERATORS: ClassVar[dict[str, str]] = {
        "sender": "from",
        "receiver": "to",
        "subject_contains": "subject",
        "body_contains": "",
        "tags": "label",
    }

    def to_gmail_q(self) -> str:
        parts: list[str] = []

        for field_name, operator in self._GMAIL_LIST_OPERATORS.items():
            values = getattr(self, field_name)
            if not values:
                continue
            if operator:
                clause = " ".join(f"{operator}:{v}" for v in values)
            else:
                clause = " ".join(values)
            parts.append(f"{{{clause}}}" if len(values) > 1 else clause)

        if self.after:
            parts.append(f"after:{self.after.strftime('%Y/%m/%d')}")
        if self.before:
            parts.append(f"before:{self.before.strftime('%Y/%m/%d')}")
        if self.is_read:
            parts.append("is:read")
        elif self.is_read is False:
            parts.append("is:unread")
        if self.is_starred:
            parts.append("is:starred")
        elif self.is_starred is False:
            parts.append("-is:starred")
        if self.has_attachments:
            parts.append("has:attachment")
        elif self.has_attachments is False:
            parts.append("-has:attachment")

        return " ".join(parts)

    @property
    def gmail(self) -> dict:
        return {"q": self.to_gmail_q()}