"""
smmarks_connector.models.base
==============================
Base dataclass shared by all API response models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiResponseBase:
    """
    Fields present in every SM Marks API response envelope.

    All response dataclasses inherit from this class and call
    :meth:`_base_kwargs` to extract these fields before populating their
    own attributes.
    """

    source: str
    api: str
    seconds: int
    date: str
    schoolname: str
    action: str
    status: str

    @classmethod
    def _base_kwargs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract the seven base envelope fields from a raw response dict.

        :param data: Raw JSON response parsed into a dictionary.
        :type data: dict[str, Any]
        :return: Keyword arguments suitable for passing to a dataclass
            constructor that inherits from :class:`ApiResponseBase`.
        :rtype: dict[str, Any]
        """
        return {
            "source":     data["source"],
            "api":        data["api"],
            "seconds":    data["seconds"],
            "date":       data["date"],
            "schoolname": data["schoolname"],
            "action":     data["action"],
            "status":     data["status"],
        }
