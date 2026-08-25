# Envel

Connects to mail sources (Gmail, Microsoft Graph, IMAP) and normalizes messages into a
unified `Envelope` model — using [Pluggle](https://github.com/hsnwhte/pluggle) as its
transform engine.

> **Status:** v0.2.0 — Alpha. Gmail is implemented and tested end to end (see
> `docs/TEST_REPORT.md`); Graph and IMAP are scaffolded but not yet functional.

## Setup

### 1. Install

```bash
pip install -e ".[dev]"
```

### 2. Gmail API credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com), create a project.
2. Enable the **Gmail API** (APIs & Services → Library).
3. Configure the **OAuth consent screen**:
    - App type: External (or Internal if using Workspace)
    - Add the `gmail.readonly` scope
    - Add your own Google account under **Test users**
4. Create an **OAuth Client ID** (APIs & Services → Credentials → Create Credentials →
   OAuth Client ID), application type **Desktop app**.
5. Download the resulting JSON and place it at `data/auth/credentials.json`.

### 3. Configure

```bash
cp query_config.yaml.example query_config.yaml
# edit query_config.yaml with your own search criteria
```

`.env` is optional — Envel falls back to sensible defaults under `data/` if it's
missing. Only copy `.env.example` to `.env` if you need to override a path or scope.

### 4. First run

```python
from envel import Envel

envel = Envel(source="gmail")

# All results matching the first search defined in query_config.yaml
results = envel.fetch_all(query_idx=0)

# A single result, by index, from the same search
one = envel.fetch_one(query_idx=0, result_idx=0)
```

On first run, a browser window opens asking you to sign in and grant access. After
granting access, a `data/auth/token.json` is written automatically — subsequent runs
won't prompt again unless the token expires and can't be refreshed.

Both `fetch_all` and `fetch_one` return plain `dict`s
(`GmailMessageFull.model_dump(mode="json")`), not Pydantic model instances — this keeps
Envel's output boundary format-agnostic for downstream consumers (e.g. a Pluggle
Transform Strategy) that shouldn't need to import Envel's internal schema.

## Testing

```bash
pytest tests/ -v
```

See `docs/TEST_REPORT.md` for the full manual and automated verification log.

## License

MIT