from datetime import date

from envel.schemas.query import SearchQuery


def test_empty_query_produces_empty_gmail_q():
    query = SearchQuery(name="empty")
    assert query.gmail == {"q": ""}


def test_single_sender_has_no_braces():
    query = SearchQuery(name="single-sender", sender=["team@upwork.com"])
    assert query.gmail == {"q": "from:team@upwork.com"}


def test_multiple_senders_use_or_braces():
    query = SearchQuery(name="multi-sender", sender=["a@upwork.com", "b@upwork.com"])
    assert query.gmail == {"q": "{from:a@upwork.com from:b@upwork.com}"}


def test_multiple_fields_are_and_joined():
    query = SearchQuery(
        name="multi-field",
        sender=["team@upwork.com"],
        subject_contains=["new job"],
    )
    assert query.gmail == {"q": "from:team@upwork.com subject:new job"}


def test_receiver_maps_to_to_operator():
    query = SearchQuery(name="receiver", receiver=["me@gmail.com"])
    assert query.gmail == {"q": "to:me@gmail.com"}


def test_body_contains_has_no_operator_prefix():
    query = SearchQuery(name="body", body_contains=["urgent"])
    assert query.gmail == {"q": "urgent"}


def test_tags_map_to_label_operator():
    query = SearchQuery(name="tags", tags=["upwork-alerts"])
    assert query.gmail == {"q": "label:upwork-alerts"}


def test_after_date_uses_slash_format():
    query = SearchQuery(name="after", after=date(2026, 8, 1))
    assert query.gmail == {"q": "after:2026/08/01"}


def test_before_date_uses_slash_format():
    query = SearchQuery(name="before", before=date(2026, 8, 1))
    assert query.gmail == {"q": "before:2026/08/01"}


def test_is_read_true_maps_to_is_read():
    query = SearchQuery(name="read", is_read=True)
    assert query.gmail == {"q": "is:read"}


def test_is_read_false_maps_to_is_unread():
    query = SearchQuery(name="unread", is_read=False)
    assert query.gmail == {"q": "is:unread"}


def test_is_read_none_is_omitted():
    query = SearchQuery(name="no-read-filter")
    assert "is:read" not in query.gmail["q"]
    assert "is:unread" not in query.gmail["q"]


def test_has_attachments_true_maps_to_has_attachment():
    query = SearchQuery(name="attachments", has_attachments=True)
    assert query.gmail == {"q": "has:attachment"}


def test_has_attachments_false_maps_to_negated():
    query = SearchQuery(name="no-attachments", has_attachments=False)
    assert query.gmail == {"q": "-has:attachment"}
