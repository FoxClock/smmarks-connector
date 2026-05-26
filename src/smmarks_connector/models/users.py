"""smmarks_connector.models.users — User and AuthenticationResponse dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import ApiResponseBase


@dataclass
class User:
    """
    Represents a Markbook Online user account.

    Returned by: ``userlist``
    """

    key: int
    name: str
    loginid: str
    email: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> User:
        return cls(
            key=data["key"],
            name=data["name"],
            loginid=data["loginid"],
            email=data["email"],
        )


@dataclass
class AuthenticationResponse(ApiResponseBase):
    """
    Envelope returned by the ``POST /authenticate.lc`` endpoint.

    Note: This response is handled inline by
    :meth:`~smmarks_connector.client.MarkbookApiClient.authenticate`
    rather than being returned directly to callers.
    """

    session_token: str
    session_key: int

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> AuthenticationResponse:
        return cls(
            **ApiResponseBase._base_kwargs(data),
            session_token=data["sessiontoken"],
            session_key=data["sessionkey"],
        )
