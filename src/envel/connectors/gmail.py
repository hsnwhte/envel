import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from envel.exceptions import errors
from envel.schemas.gmail import GmailMessageFull
from envel.schemas.query import SearchQuery
from envel.settings import CREDENTIALS_PATH, DEFAULT_GMAIL_SCOPES, TOKEN_PATH

logger = logging.getLogger(__name__)


class GmailConnector:
    def __init__(self, auto_auth: bool = True, scopes:list[str] | None = None):
        self.auto_auth = auto_auth
        self._connected = False
        self.scopes = scopes or DEFAULT_GMAIL_SCOPES
        self.creds = None

    def fetch(
            self,
            search_query: SearchQuery
    ) -> list[GmailMessageFull]:
        if not self._connected:
            if self.auto_auth:
                self.authenticate()
            else:
                raise errors.NotAuthenticatedError(
                    "Connector not authenticated."
                )
        service = build("gmail", "v1", credentials=self.creds)
        try:
            response = service.users().messages().list(userId="me", **search_query.gmail).execute()
        except HttpError as e:
            raise errors.GmailFetchError(f"Failed to list messages: {e}") from e

        message_refs = response.get("messages", [])
        results: list[GmailMessageFull] = []
        failed_count = 0
        for ref in message_refs:
            try:
                raw = (
                    service.users()
                    .messages()
                    .get(userId="me", id=ref["id"], format="full")
                    .execute()
                )
                results.append(GmailMessageFull(**raw))
            except HttpError as e:
                failed_count += 1
                logger.warning("Failed to fetch message %s: %s", ref["id"], e)

        logger.info(
            "Fetched %d/%d messages (%d failed)", len(results), len(message_refs), failed_count
        )

        return results



    def authenticate(self):
        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), self.scopes)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH), self.scopes
                )
                creds = flow.run_local_server(port=0)
            except FileNotFoundError as e:
                raise errors.CredentialsFileError(
                    f"Credentials file not found: {e}"
                ) from e
        self.creds = creds
        self._connected = True
        TOKEN_PATH.write_text(creds.to_json())
