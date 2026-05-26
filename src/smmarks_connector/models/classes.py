"""smmarks_connector.models.classes — Class dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Class:
    """
    Represents a class (teaching group) within a markbook.

    Returned by: ``getmarkbook``, ``getmarkbookalt``, ``getoutcomes*``
    """

    key: int
    name: str
    teachername1: str
    teachername2: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Class:
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            teachername1=data.get("teachername1"),
            teachername2=data.get("teachername2"),
        )
