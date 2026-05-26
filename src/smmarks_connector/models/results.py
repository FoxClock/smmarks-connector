"""smmarks_connector.models.results — Result dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    """
    A single task result for a single student.

    Returned by: ``getmarkbookalt``
    """

    studentkey: int
    taskkey: int
    rawresult: str
    roundedresult: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Result:
        return cls(
            studentkey=data["studentkey"],
            taskkey=data["taskkey"],
            rawresult=data["rawresult"],
            roundedresult=data["roundedresult"],
        )
