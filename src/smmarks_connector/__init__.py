"""
smmarks-connector
=================
A Python client library for the SM Marks (Markbook Online) API.

Quickstart::

    from smmarks_connector import MarkbookApiClient, InitialAuthStrategy, configure

    configure()   # activate default log redaction

    client = MarkbookApiClient(
        baseUrl="https://marks.school.edu.au",
        authStrat=InitialAuthStrategy("user", "pass"),
        api_key="key",
    )
    client.authenticate()
    markbooks = client.get_markbook_summary()
"""

from .auth.strategy import InitialAuthStrategy, OngoingAuthStrategy
from .client import MarkbookApiClient
from .logger import configure

__version__ = "0.1.0"

__all__ = [
    "MarkbookApiClient",
    "InitialAuthStrategy",
    "OngoingAuthStrategy",
    "configure",
    "__version__",
]
