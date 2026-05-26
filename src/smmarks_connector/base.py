"""
smmarks_connector.base
=======================
Base HTTP layer for the SM Marks API client.

Handles request construction, auth-parameter injection, response
deserialisation, and structured logging.  All log messages are emitted
at standard levels (``DEBUG`` for outgoing requests, ``INFO`` for
responses, ``ERROR`` on failure) so the consuming application controls
verbosity through normal logging configuration.
"""

from __future__ import annotations

import json
import re
from typing import Any

import requests

from .auth.base import AuthStrategy
from .logger import get_logger, scrub

_logger = get_logger("api")


class ApiBase:
    """
    Base class that provides a thin, authenticated HTTP session over the SM
    Marks API.

    Subclasses receive a fully constructed :class:`requests.Session` and call
    :meth:`request` to make authenticated API calls without worrying about
    auth-parameter injection or response normalisation.

    :param baseUrl: Root URL of the SM Marks instance, e.g.
        ``"https://marks.school.edu.au"``.  Trailing slashes are stripped.
    :type baseUrl: str
    :param authStrat: Initial authentication strategy.  Replaced by
        :class:`~smmarks_connector.auth.strategy.OngoingAuthStrategy` after a
        successful login.
    :type authStrat: AuthStrategy
    """

    VALID_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    def __init__(self, baseUrl: str, authStrat: AuthStrategy) -> None:
        if not baseUrl:
            raise ValueError("Base URL not set correctly.")

        if not authStrat or not isinstance(authStrat, AuthStrategy):
            raise ValueError("API client must have an Authorisation strategy.")

        self.baseUrl: str = baseUrl.rstrip("/")
        self.authStrategy: AuthStrategy = authStrat
        self.session: requests.Session = requests.Session()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_method(self, method: str) -> bool:
        """Return ``True`` if *method* is a recognised HTTP verb."""
        return method.upper() in self.VALID_METHODS

    # ------------------------------------------------------------------
    # Public request interface
    # ------------------------------------------------------------------

    def request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """
        Execute an authenticated HTTP request and return the parsed response.

        Authentication parameters from the active
        :class:`~smmarks_connector.auth.base.AuthStrategy` are merged into
        the query string for GET requests and into the POST body via
        :meth:`~smmarks_connector.auth.base.AuthStrategy.get_auth_params`.
        Callers that pass ``data=`` (POST bodies) must merge auth params
        themselves before this point if required by the endpoint — see
        :meth:`~smmarks_connector.client.MarkbookApiClient.create_markbook`.

        The SM Marks API sometimes returns trailing commas in JSON arrays
        and objects.  These are stripped before parsing.

        :param method: HTTP verb (case-insensitive).  Must be one of
            ``VALID_METHODS``.
        :type method: str
        :param endpoint: Path relative to :attr:`baseUrl`.  Leading slashes
            are stripped.
        :type endpoint: str
        :param kwargs: Additional keyword arguments forwarded to
            :meth:`requests.Session.request` (e.g. ``params``, ``data``).
        :return: Parsed JSON response as a dictionary.
        :rtype: dict[str, Any]
        :raises ValueError: If *method* is not a valid HTTP verb.
        :raises requests.HTTPError: If the server returns a 4xx or 5xx status.
        """
        if not self._validate_method(method):
            raise ValueError(
                f"Only valid methods can be used. "
                f"current: {method!r} | valid: {self.VALID_METHODS}"
            )

        # Inject auth params into the query string.
        params: dict[str, Any] = kwargs.get("params", {})
        params.update(self.authStrategy.get_auth_params())
        kwargs["params"] = params

        url = f"{self.baseUrl}/{endpoint.lstrip('/')}"
        action = params.get("action", endpoint)

        _logger.debug(
            "API request",
            extra={
                "data": {
                    "method": method,
                    "url": url,
                    "action": action,
                    "params": scrub(params),
                    "body": scrub(kwargs.get("data", {})),
                }
            },
        )

        try:
            response = self.session.request(method=method, url=url, **kwargs)
            response.raise_for_status()
        except Exception as exc:
            _logger.error(
                "API request failed",
                extra={
                    "data": {
                        "method": method,
                        "url": url,
                        "action": action,
                        "error": str(exc),
                    }
                },
                exc_info=True,
            )
            raise

        # Strip trailing commas that the SM Marks API sometimes emits.
        sanitized = re.sub(r",\s*([}\]])", r"\1", response.text)
        parsed: dict[str, Any] = json.loads(sanitized)

        _logger.info(
            "API response",
            extra={
                "data": {
                    "method": method,
                    "action": action,
                    "http_status": response.status_code,
                    "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 2),
                    "api_status": parsed.get("status"),
                }
            },
        )

        return parsed
