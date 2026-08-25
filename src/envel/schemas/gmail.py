import base64

from pydantic import BaseModel, Field, field_validator


class MessageHeader(BaseModel):
    name: str = ""
    value: str = ""

class MessageBody(BaseModel):
    attachmentId: str = ""
    size: int = 0
    data: str = ""

    @field_validator("data", mode="after")
    @classmethod
    def decode_base64(cls, value:str) ->str:
        if not value:
            return value
        decoded = base64.urlsafe_b64decode(value)
        return decoded.decode("utf-8")

class MessagePart(BaseModel):
    partId: str = ""
    mimeType: str = ""
    filename: str = ""
    headers: list[MessageHeader] = Field(default_factory=list)
    body: MessageBody = Field(default_factory=lambda: MessageBody(size=0))
    parts: list["MessagePart"] = Field(default_factory=list)



class GmailMessageFull(BaseModel):
    id: str
    threadId: str
    labelIds: list[str] = Field(default_factory=list)
    snippet: str = ""
    historyId: str
    internalDate: str
    payload: MessagePart
    sizeEstimate: int

