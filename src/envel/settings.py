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
CREDENTIALS_PATH.mkdir(parents=True, exist_ok=True)

DEFAULT_TOKEN_PATH = RUNTIME_ROOT / "data" / "auth" / "token.json"
TOKEN_PATH = Path(os.environ.get("ENVEL_TOKEN_PATH", DEFAULT_TOKEN_PATH))
TOKEN_PATH.mkdir(parents=True, exist_ok=True)

# ----- Query Config
DEFAULT_QUERY_CONFIG_PATH = RUNTIME_ROOT / "data" / "query_config.yaml"
QUERY_CONFIG_PATH = Path(
    os.environ.get("ENVEL_QUERY_CONFIG_PATH", DEFAULT_QUERY_CONFIG_PATH)
)
QUERY_CONFIG_PATH.mkdir(parents=True, exist_ok=True)

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