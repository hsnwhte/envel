from envel.connectors.gmail import GmailConnector
from envel.factories.query import load_search_query
from envel.settings import GMAIL_SCOPES, QUERY_CONFIG_PATH, RAW_OUTPUT_DIR, SUPPORTED_MAIL_SOURCES
from typing import Literal
from envel.exceptions import errors

MailSource = Literal["gmail", "graph", "imap"]

class Envel:
    def __init__(self, source:MailSource="gmail"):
        if source not in SUPPORTED_MAIL_SOURCES:
            raise errors.SourceNotSupportedError(
                f"Source '{source}' is not a supported format. "
                f"HINT: it must be one of {SUPPORTED_MAIL_SOURCES}.")

        if source == "gmail":
            self.connector = GmailConnector(scopes=GMAIL_SCOPES)
        elif source == "graph":
            raise NotImplementedError("Graph connector is not implemented yet.")
        elif source == "imap":
            raise NotImplementedError("IMAP connector is not implemented yet.")


    def fetch_all(self, query_idx:int):
        search_query = load_search_query(index=query_idx, config_file=str(QUERY_CONFIG_PATH))
        return self.connector.fetch(search_query)

    def fetch_one(self, query_idx: int, result_idx:int):
        search_query = load_search_query(index=query_idx, config_file=str(QUERY_CONFIG_PATH))
        return self.connector.fetch(search_query)[result_idx]


