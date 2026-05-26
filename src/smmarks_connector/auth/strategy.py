"""
smmarks_connector.auth.strategy
================================
Concrete authentication strategies for the SM Marks API.

Two strategies cover the full authentication lifecycle:

* :class:`InitialAuthStrategy` — used for the very first ``authenticate.lc``
  POST, which requires plain credentials.
* :class:`OngoingAuthStrategy` — used for all subsequent requests once a
  session token and key have been obtained.
"""

from __future__ import annotations

from typing import Any

from .base import AuthStrategy


class InitialAuthStrategy(AuthStrategy):
    """
    Authenticates using plain API credentials.

    Used exclusively for the initial ``POST /authenticate.lc`` call.
    After a successful response the client replaces this strategy with
    :class:`OngoingAuthStrategy`.

    :param username: API username.
    :type username: str
    :param password: API password.
    :type password: str
    """

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    def get_auth_params(self) -> dict[str, Any]:
        return {
            "apiuser": self.username,
            "apipassword": self.password,
        }


class OngoingAuthStrategy(AuthStrategy):
    """
    Authenticates using a session token, session key, and API key.

    Instantiated automatically by :class:`~smmarks_connector.client.MarkbookApiClient`
    after a successful :meth:`~smmarks_connector.client.MarkbookApiClient.authenticate`
    call.

    :param token: Session token returned by the authentication endpoint.
    :type token: str
    :param key: Session key returned by the authentication endpoint.
    :type key: int
    :param apikey: Static API key issued to the integration.
    :type apikey: str
    """

    def __init__(self, token: str, key: int, apikey: str) -> None:
        self.token = token
        self.key = key
        self.apikey = apikey

    def get_auth_params(self) -> dict[str, Any]:
        return {
            "sessiontoken": self.token,
            "sessionkey": str(self.key),
            "apikey": self.apikey,
        }
