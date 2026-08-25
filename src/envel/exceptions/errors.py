class EnvelError(Exception): ...


class QueryConfigFileError(EnvelError):
    """Errors related to 'query_config.yaml' file."""


class PipelineError(EnvelError):
    """Errors related to the phases of pipeline flow"""


class SourceNotSupportedError(PipelineError):
    """Raised when the provided mail service provider is not supported."""


class ConnectorError(EnvelError):
    """Errors related to Connectors"""


class CredentialsFileError(EnvelError):
    """Errors related to 'credentials.json' file."""


class NotAuthenticatedError(ConnectorError):
    """Raised when the connector is not authenticated."""


class GmailFetchError(ConnectorError):
    """Raised when the initial message-list fetch from Gmail fails."""
