# smmarks-connector

A Python client library for the SM Marks (Markbook Online) API.

## Installation

```bash
pip install smmarks-connector
```

With uv:

```bash
uv add smmarks-connector
```

## Quick Start

```python
import logging
from smmarks_connector import MarkbookApiClient, InitialAuthStrategy, configure

# 1. (Optional) Configure log redaction before doing anything else.
#    Passing no arguments applies the built-in sensitive-field defaults.
configure()

# 2. Wire up your application's logging as normal — the library emits
#    no output unless you attach a handler.
logging.basicConfig(level=logging.INFO)

# 3. Build the client and authenticate.
client = MarkbookApiClient(
    baseUrl="https://your-smmarks-instance.example.com",
    authStrat=InitialAuthStrategy("username", "password"),
    api_key="your-api-key",
)
client.authenticate()

# 4. Call the API.
markbooks = client.get_markbook_summary()
for mb in markbooks.list:
    print(mb.name, mb.year)
```

## Logging

smmarks-connector uses Python's standard `logging` module under the
`smmarks_connector` logger hierarchy. The library **does not attach any
handlers** — that is the responsibility of your application.

```python
import logging

# Show all library output at DEBUG level.
logging.getLogger("smmarks_connector").setLevel(logging.DEBUG)
```

### Redaction

Sensitive field values (passwords, tokens, keys) are scrubbed before they
are passed to any log call. Call `configure()` once at application startup
to control which fields are redacted:

```python
from smmarks_connector import configure

# Use built-in defaults:
#   apiuser, apipassword, sessiontoken, sessionkey, apikey
configure()

# Override with your own field list:
configure(redact_fields=["mypassword", "mytoken"])

# Disable redaction entirely:
configure(redact_fields=[])
```

You can also attach `ScrubFilter` directly to any handler for defence-in-depth:

```python
from smmarks_connector.logger import ScrubFilter, DEFAULT_REDACT_FIELDS

handler = logging.StreamHandler()
handler.addFilter(ScrubFilter(DEFAULT_REDACT_FIELDS))
logging.getLogger("smmarks_connector").addHandler(handler)
```

## Development

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run tests with coverage
uv run pytest

# Lint
uv run ruff check src tests

# Format
uv run ruff format src tests
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
