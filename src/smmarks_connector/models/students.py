"""smmarks_connector.models.students — student dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class StudentBase:
    """
    Core student identity fields shared by all student-bearing endpoints.
    """

    key: int
    studentid: str
    familyname: str
    givename: str
    preferredname: str
    classkey: int
    classname: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> StudentBase:
        return cls(
            key=data["key"],
            studentid=data["studentid"],
            familyname=data["familyname"],
            givename=data["givename"],
            preferredname=data["preferredname"],
            classkey=data["classkey"],
            classname=data["classname"],
        )


@dataclass
class StudentWithResults(StudentBase):
    """
    Student extended with per-task result arrays.

    Returned by: ``getmarkbook``
    """

    rawresults: list[str]
    roundedresults: list[str]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> StudentWithResults:
        base = StudentBase.from_json(data)
        return cls(
            **base.__dict__,
            rawresults=data["rawresults"],
            roundedresults=data["roundedresults"],
        )


@dataclass
class StudentWithOutcomes(StudentBase):
    """
    Student extended with per-outcome achievement levels.

    Returned by: ``getoutcomes``
    """

    outcomelevels: list[str]
