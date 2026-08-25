### 📅 2026-08-25, Tuesday

**11:35** | *[BUILD]*

Built out Envel's Gmail path end to end today: OAuth (InstalledAppFlow, token
persistence, refresh-before-reauth ordering), a source-agnostic `SearchQuery` model with
a `.gmail` property that translates fields into Gmail's query syntax (OR within a field
via curly braces, AND across fields), a recursive `MessagePart`/`GmailMessageFull`
schema matching Gmail's actual API shape, and a `field_validator` on `MessageBody.data`
that transparently decodes base64 at model-construction time — callers never see encoded
data.

Made and reversed several decisions along the way, each for a reason worth remembering.
Dropped per-format Gmail models (minimal/metadata/full/raw) and the `@overload` approach
after concluding the actual need was always `full` — decided the type-safety ceremony
(four overload signatures repeating one real implementation) wasn't worth it for a
feature I'll never use; this cut real code, not just deferred it. Rejected putting
Gmail's format concept into `SearchQuery` for the same underlying reason as the
`labels`/`categories` merge into `tags`: source-specific concepts don't belong in a
source-agnostic schema. Reversed an early decision to make `receiver`/`sender` scalar
strings — they needed to be lists to support OR-matching multiple addresses, caught only
when a real query file failed validation.

Settled the "engine vs. convenience" tension by keeping both layers: `envel/__init__.py`
re-exports `GmailConnector`, `SearchQuery`, `load_search_query` for anyone who wants to
assemble the pipeline by hand, while a new `Envel` class in `client.py` wraps connector
selection (`source: Literal["gmail","graph","imap"]`, validated against
`SUPPORTED_MAIL_SOURCES` at runtime), query loading, and fetch into one object —
`graph`/`imap` raise `NotImplementedError` rather than silently no-op. `fetch_one` is a
known inefficiency (fetches everything, then indexes) — acceptable for alpha, revisit if
it matters later.

Own exception hierarchy is holding up: `QueryConfigFileError` for the four YAML-loading
failure modes (file missing, malformed YAML, index out of range, schema validation), and
today added `GmailCredentialsNotFoundError` after noticing a raw `FileNotFoundError`
from Google's library was leaking past `authenticate()` unwrapped — caught it, wrapped
it with a message pointing at Cloud Console setup.

Tested against a real Upwork job-alert email end to end (Gmail Cloud Console project,
OAuth consent screen, test user, Desktop app credentials) — full round trip works:
`Envel(source="gmail").fetch_all(query_idx=0)` returns parsed, validated
`GmailMessageFull` objects with decoded bodies. Also manually verified the failure
paths: deleting `query_config.yaml` throws the expected config error; deleting
`credentials.json` + `token.json` throws the expected credentials error; deleting only
`.env` doesn't break anything (confirms the documented "all settings optional, sensible
defaults" claim actually holds).

Not yet done: Pluggle handoff (Transform Strategy to turn the raw header/body soup into
something usable), Graph/IMAP connectors, README setup walkthrough (written today, see
below).

**14:36** | *[MILESTONE v0.2.0]*

Closed out the Gmail path for v0.2.0. Wrote 34 pytest tests across four files —
`SearchQuery.gmail` translation (OR-within-field via braces, AND-across-fields,
three-state booleans, date formatting), the recursive `MessagePart`/`GmailMessageFull`
schema and its base64-decoding `field_validator`, `load_search_query`'s five failure
modes plus two success paths, and `Envel`'s source dispatch (`SourceNotSupportedError`,
`NotImplementedError` stubs for graph/imap). Deliberately scoped out
`GmailConnector.fetch()`/`authenticate()` — those need mocking `googleapiclient`,
deferred to a later pass rather than blocking this release on it.

First run caught one real bug (`sender`/`receiver` typed as `str | None` when the actual
use case — and the query config itself — needed `list[str]` for OR-matching) and one
test-design shortcoming of my own making: I wrote `test_multiple_fields_are_and_joined`
expecting `subject:(new job)` for a single-value field, but `to_gmail_q()` only
parenthesizes when a field has *multiple* values (OR-bracing), so a lone value is
written bare. Fixed the assertion, not the code — the code was right. Left an open
question in `TEST_REPORT.md`: does Gmail's real search box parse a bare multi-word value
like `subject:new job` as one phrase or two ANDed terms? Not yet verified against the
actual search box.

Also did the manual end-to-end pass I'd been deferring: real Google Cloud Console
project, OAuth consent screen, Desktop app credentials, and a fetch against a real
Upwork job-alert email sitting in my own inbox. Full round trip worked — recursive
`parts` structure matched expectations, `body.data` came back decoded, not base64. Along
the way, `authenticate()` was missing `self.creds = creds` and `self._connected = True`
after a refactor (caught via a plain `AttributeError`, not subtle), and a raw
`FileNotFoundError` from `InstalledAppFlow` was leaking past `authenticate()` unwrapped
when `credentials.json` was missing — wrapped it into `CredentialsFileError`, consistent
with `QueryConfigFileError`'s existing pattern. Manually deleting each of `.env`,
`query_config.yaml`, and the credentials pair one at a time confirmed the expected
failure/fallback behavior for each — `.env` alone is genuinely optional, the other two
are hard requirements with clean error messages.

Landed on a real "is Pluggle even the right tool here" moment mid-session, while
starting the `gmail_message_parser` Transform Strategy. Pluggle's core contract is
deliberately narrow — `TransformableData(content: bytes, origin_format)` in,
`TransformedData(content: bytes)` out, no awareness of any domain shape — which is the
whole point of keeping Pluggle domain-agnostic, but it means every strategy re-does its
own encode/decode/parse work with no shortcuts. Recognized this as a real tradeoff
between technical minimalism and portfolio value (more Pluggle strategies, more commits,
more visible ecosystem depth) rather than a purely technical question, and consciously
chose to keep using Pluggle for that reason — decided the strategy will construct
`GmailMessageFull` from the raw bytes for its own internal type safety, then reduce to a
plain dict for its actual output, keeping Envel's own boundary (Pluggle doesn't know
Envel exists) and the strategy's boundary (outputs a dict, not an Envel type) both
clean. Wrote up a short backlog note for Pluggle itself: `StrategyMeta` could eventually
grow an optional `dependencies` field so a strategy can declare (and Pluggle can at
least warn about) packages it needs beyond Pluggle's own — not building it now, `envel`
's dependency on Pluggle strategies being "the user's problem" stays a deliberate,
accepted tradeoff for now.

Simplified `Envel.fetch_all`/`fetch_one` to return `dict` (`model_dump(mode="json")`)
rather than `GmailMessageFull` instances — this is what lets the Transform Strategy
consume Envel's output without importing Envel's schema directly once it's writing to a
file/bytes boundary for Pluggle. Bootstrap.py got deleted — the "is a strategy installed
in Pluggle" concern turned out to not be Envel's job at all; that belongs to whatever
application (`my-upwork-alert`) actually uses Envel and Pluggle together.

`README.md` and `TEST_REPORT.md` (new, mirroring Pluggle's own format) written and
committed. `gmail_message_parser_v1.0` strategy itself deferred to later today —
priority is finishing `my-upwork-alert`'s own skeleton first, per my own "don't scatter"
instinct catching itself mid-session for once.