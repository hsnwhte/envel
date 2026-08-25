import os
from pathlib import Path

from dotenv import load_dotenv
from pluggle.enums import ContentFormat

### --- SYSTEM ADDRESSES
# ----- Project Root
RUNTIME_ROOT = Path.cwd()
# ----- Environment
load_dotenv()

# ----- Mail Source Selection
# "gmail" | "graph" | "imap" — sadece "gmail" implemente edildi (bkz. connectors/)
MAIL_SOURCE = os.environ.get("ENVEL_MAIL_SOURCE", "gmail")

# ----- Gmail / Graph Auth
DEFAULT_CREDENTIALS_PATH = RUNTIME_ROOT / "data" / "auth" / "credentials.json"
CREDENTIALS_PATH = Path(
    os.environ.get("ENVEL_CREDENTIALS_PATH", DEFAULT_CREDENTIALS_PATH)
)
CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_TOKEN_PATH = RUNTIME_ROOT / "data" / "auth" / "token.json"
TOKEN_PATH = Path(os.environ.get("ENVEL_TOKEN_PATH", DEFAULT_TOKEN_PATH))
TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

# ----- Query Config
DEFAULT_QUERY_CONFIG_PATH = RUNTIME_ROOT / "query_config.yaml"
QUERY_CONFIG_PATH = Path(
    os.environ.get("ENVEL_QUERY_CONFIG_PATH", DEFAULT_QUERY_CONFIG_PATH)
)

# ----- Logs
DEFAULT_LOG_DIR = RUNTIME_ROOT / "data" / "logs" / "envel"
LOG_DIR = Path(os.environ.get("ENVEL_LOG_DIR", DEFAULT_LOG_DIR))
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ----- Pipeline Output
DEFAULT_RAW_OUTPUT_DIR = RUNTIME_ROOT / "data" / "output" / "envel"
RAW_OUTPUT_DIR = Path(os.environ.get("ENVEL_RAW_OUTPUT_DIR", DEFAULT_RAW_OUTPUT_DIR))
RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- System variables
NORMALIZED_FORMAT = ContentFormat.JSON
SUPPORTED_MAIL_SOURCES = ["gmail", "graph", "imap"]

# --- Service Provider Scopes
DEFAULT_GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_SCOPES = os.environ.get("ENVEL_GMAIL_SCOPES")
GMAIL_SCOPES = GMAIL_SCOPES.split(",") if GMAIL_SCOPES else DEFAULT_GMAIL_SCOPES
