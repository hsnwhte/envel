import pytest

from envel import Envel
from envel.connectors.gmail import GmailConnector
from envel.exceptions import errors


def test_unsupported_source_raises_source_not_supported_error():
    with pytest.raises(errors.SourceNotSupportedError):
        Envel(source="outlook")


def test_graph_source_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        Envel(source="graph")


def test_imap_source_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        Envel(source="imap")


def test_gmail_source_creates_gmail_connector():
    envel = Envel(source="gmail")
    assert isinstance(envel.connector, GmailConnector)


def test_default_source_is_gmail():
    envel = Envel()
    assert isinstance(envel.connector, GmailConnector)
