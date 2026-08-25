from typing import Protocol, TypeVar

from envel.schemas.query import SearchQuery

T = TypeVar("T")


class Connector(Protocol[T]):
    def authenticate(self) -> None:
        """Establish/refresh the connection. Idempotent — safe to call
        even if already authenticated."""
        ...

    def fetch(self, search_query: SearchQuery) -> list[T]:
        """Fetch raw, source-specific messages matching the query.

        Behavior depends on the connector's auto_authenticate setting:
        if enabled (default), calls authenticate() internally when not
        yet connected. If disabled, raises if authenticate() hasn't
        been called explicitly first.
        """
        ...
