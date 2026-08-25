# Envel — Manual & Automated Test Report

This report tracks manual end-to-end verification and automated test suite results for
each Envel release. It exists alongside `docs/DIARY.md` (development narrative) as a
focused, at-a-glance record of what has actually been verified to work — intended for
anyone evaluating the project from the outside.

Each entry below documents a single manual test run: what was tested, with what input,
what the result was, and what that confirms. Automated (pytest) results are summarized
separately at the end of each version section.

---

## v0.2.0

### Automated (pytest)

**Summary (as of 2026-08-25):**

- Total: 34 tests
- Coverage by category: `SearchQuery.gmail` translation (14), Gmail schema / base64
  decoding (8), `load_search_query` factory (7), `Envel` client source selection (5)
- Scope note: these tests cover pure logic (query-string translation, base64 decoding,
  YAML-loading error paths, source dispatch) and do not exercise
  `GmailConnector.fetch()`
  or `authenticate()` against a live or mocked Gmail API — that coverage is deferred to
  a later pass (would require mocking `googleapiclient`).

#### Test run 1

- Total tests: 34
- Failed: 0
- Passed: 34
- Test Design Shortcomings: 1 (fixed before this run)
    1. `test_multiple_fields_are_and_joined` initially asserted `subject:(new job)` for
       a single-element `subject_contains` list, but `to_gmail_q()` only wraps a field's
       joined clause in `{}` when it has *multiple* values (for OR-matching) — a single
       value is written bare, without parentheses. Test expectation didn't match actual
       (correct) behavior; fixed the assertion to `subject:new job`.
    2. Open question, not yet resolved: does Gmail's real search syntax parse a
       multi-word bare value like `subject:new job` as "subject contains 'new job'", or
       as two separate conditions (`subject:new` AND anywhere `job`)? `to_gmail_q()`
       doesn't currently wrap single multi-word values in parentheses — worth verifying
       against Gmail's actual search box before relying on this for anything beyond
       single-word terms.

### Manual verification

**Summary (as of 2026-08-25):** First end-to-end verification of the Gmail path, run
against a real Google Cloud Console project and a real Upwork job-alert email in the
developer's own inbox.

#### Test 1 — OAuth flow, first-time authorization

- **Input:** Fresh `credentials.json` (Desktop app, downloaded from Google Cloud
  Console), no existing `token.json`
- **Command:** `GmailConnector().authenticate()` (PyCharm console)
- **Verifies:** `InstalledAppFlow.from_client_secrets_file()` → local server → browser
  consent → `Credentials` object → `token.json` persisted to disk
- **Result:** PASS (after one fix) — first attempt raised
  `AttributeError: 'GmailConnector' object has no attribute 'creds'`. Cause: `self.creds
  = creds` and `self._connected = True` were dropped from the guided rewrite of
  `authenticate()`. Fixed by re-adding both assignments; re-run succeeded,
  `creds.valid` returned `True` and `data/auth/token.json` was written.

#### Test 2 — Full fetch against a real Gmail inbox

- **Input:** `query_config.yaml` with one search (`sender: donotreply@upwork.com`,
  `subject_contains: "job alert"`), a real Upwork job-alert email present in the inbox
- **Command:** `Envel(source="gmail").fetch_all(query_idx=0)` (via PyCharm console,
  later via a standalone script)
- **Verifies:** `SearchQuery.gmail` → `messages.list` → `messages.get(format="full")` →
  `GmailMessageFull` construction → `MessageBody.data` base64 auto-decode (via
  `field_validator`)
- **Result:** PASS — one real message returned, recursive `MessagePart`/`parts`
  structure matched the expected shape (`multipart/alternative` with `text/plain` and
  `text/html` children), `body.data` on both leaf parts was decoded to readable text,
  not base64.
- **Bug found and fixed along the way:** `SearchQuery.sender` / `.receiver` were
  originally typed as `str | None`, but the query config (and the field's actual use
  case — OR-matching multiple addresses) requires a list. A real config file with
  `sender:` as a YAML list failed `ValidationError` until the fields were corrected to
  `list[str]`.

#### Test 3 — Missing `query_config.yaml`

- **Input:** `query_config.yaml` deleted
- **Command:** `Envel(source="gmail").fetch_all(query_idx=0)`
- **Verifies:** `load_search_query`'s `FileNotFoundError` → `QueryConfigFileError`
  wrapping
- **Result:** PASS (expected) — clean `QueryConfigFileError` with the intended message,
  no raw traceback surfaced to the caller.

#### Test 4 — Missing `credentials.json` and `token.json`

- **Input:** Both `data/auth/credentials.json` and `data/auth/token.json` deleted
- **Command:** `Envel(source="gmail").fetch_all(query_idx=0)`
- **Verifies:** `authenticate()`'s handling of a from-scratch OAuth attempt with no
  credentials file available
- **Result:** FAIL (first run) — a raw `FileNotFoundError` from
  `InstalledAppFlow.from_client_secrets_file()` propagated unwrapped past
  `authenticate()`, contradicting the project's own exception-hierarchy discipline.
  **Fixed:** wrapped the call in `try/except FileNotFoundError`, re-raising as
  `errors.CredentialsFileError`. Re-run confirmed the wrapped exception surfaces
  correctly.

#### Test 5 — Missing `.env` only

- **Input:** `.env` deleted, `credentials.json`/`token.json`/`query_config.yaml` all
  left in place
- **Command:** `Envel(source="gmail").fetch_all(query_idx=0)`
- **Verifies:** the "all settings optional, sensible defaults under `data/`" claim in
  `.env.example`
- **Result:** PASS — no behavior change; every `os.environ.get(...)` fallback in
  `settings.py` held as documented.

#### Test 6 — Unsupported / unimplemented sources

- **Input:** `source="outlook"`, `source="graph"`, `source="imap"`
- **Command:** `Envel(source=...)`
- **Verifies:** `SUPPORTED_MAIL_SOURCES` validation and the `NotImplementedError` stubs
  for `graph`/`imap`
- **Result:** PASS — `"outlook"` raised `SourceNotSupportedError` as expected;
  `"graph"`/`"imap"` each raised `NotImplementedError` rather than silently constructing
  a broken `Envel` instance.