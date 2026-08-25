import base64

from envel.schemas.gmail import (
    GmailMessageFull,
    MessageBody,
    MessageHeader,
    MessagePart,
)


def _encode(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("utf-8")


def test_message_body_decodes_base64_on_construction():
    body = MessageBody(data=_encode("hello world"))
    assert body.data == "hello world"


def test_message_body_empty_data_stays_empty():
    body = MessageBody(data="")
    assert body.data == ""


def test_message_body_default_data_is_empty_string():
    body = MessageBody()
    assert body.data == ""


def test_message_part_top_level_body_is_decoded():
    part = MessagePart(body=MessageBody(data=_encode("plain text")))
    assert part.body.data == "plain text"


def test_message_part_nested_parts_are_decoded():
    part = MessagePart(
        mimeType="multipart/alternative",
        parts=[
            MessagePart(mimeType="text/plain", body=MessageBody(data=_encode("plain"))),
            MessagePart(
                mimeType="text/html", body=MessageBody(data=_encode("<p>html</p>"))
            ),
        ],
    )
    assert part.parts[0].body.data == "plain"
    assert part.parts[1].body.data == "<p>html</p>"


def test_message_part_deeply_nested_parts_are_decoded():
    part = MessagePart(
        parts=[MessagePart(parts=[MessagePart(body=MessageBody(data=_encode("deep")))])]
    )
    assert part.parts[0].parts[0].body.data == "deep"


def test_gmail_message_full_builds_from_raw_dict():
    raw = {
        "id": "abc123",
        "threadId": "abc123",
        "labelIds": ["INBOX", "UNREAD"],
        "snippet": "a short preview",
        "historyId": "999",
        "internalDate": "1787637827000",
        "sizeEstimate": 100,
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "sender@example.com"},
            ],
            "body": {"data": _encode("body text")},
        },
    }
    message = GmailMessageFull(**raw)
    assert message.id == "abc123"
    assert message.payload.body.data == "body text"
    assert message.payload.headers[0].name == "Subject"


def test_message_header_default_values():
    header = MessageHeader()
    assert header.name == ""
    assert header.value == ""
