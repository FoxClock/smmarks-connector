"""
smmarks_connector.auth.base
===========================
Abstract base class for authentication strategies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AuthStrategy(ABC):
    """
    Interface that all authentication strategies must implement.

    A strategy is responsible for returning the query-string or POST-body
    parameters required to authenticate a single API request.  The concrete
    strategy in use can be swapped at runtime (e.g. when transitioning from
    initial credentials to session-token auth after a successful login).
    """

    @abstractmethod
    def get_auth_params(self) -> dict[str, Any]:
        """
        Return a dictionary of authentication parameters for the current
        request.

        :return: Key/value pairs to be merged into the request parameters
            or POST body.
        :rtype: dict[str, Any]
        """
