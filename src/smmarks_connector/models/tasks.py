"""smmarks_connector.models.tasks — Task dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    """
    Represents an assessment task within a markbook.

    Returned by: ``getmarkbook``, ``getmarkbookalt``
    """

    key: int
    name: str
    maximum: int
    decimalplaces: int

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Task:
        return cls(
            key=data["key"],
            name=data["name"],
            maximum=data["maximum"],
            decimalplaces=data["decimalplaces"],
        )
