"""
smmarks_connector.models.responses
====================================
Typed response envelopes for every SM Marks API action.

Each class inherits from :class:`~smmarks_connector.models.base.ApiResponseBase`
and exposes a ``from_json`` factory method that deserialises a raw parsed-JSON
dictionary into a fully typed Python object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import ApiResponseBase
from .classes import Class
from .markbooks import Markbook, MarkbookAlt, MarkbookSummary
from .outcomes import Outcome, OutcomeLevel
from .results import Result
from .students import StudentBase, StudentWithOutcomes, StudentWithResults
from .tasks import Task
from .users import User
from .utils import parse_list


@dataclass
class UserListResponse(ApiResponseBase):
    """Returned by: ``userlist``"""

    list: list[User]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> UserListResponse:
        return cls(
            **ApiResponseBase._base_kwargs(data),
            list=parse_list(data["list"], User),
        )


@dataclass
class MarkbookListResponse(ApiResponseBase):
    """Returned by: ``markbooklist``"""

    list: list[MarkbookSummary]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> MarkbookListResponse:
        return cls(
            **ApiResponseBase._base_kwargs(data),
            list=parse_list(data["list"], MarkbookSummary),
        )


@dataclass
class GetMarkbookResponse(ApiResponseBase, Markbook):
    """
    Returned by: ``getmarkbook``

    Combines the API response envelope with the full :class:`Markbook`
    structure.
    """

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> GetMarkbookResponse:
        return cls(
            **ApiResponseBase._base_kwargs(data),
            markbookkey=data["markbookkey"],
            markbookname=data["markbookname"],
            markbookyear=data["markbookyear"],
            markbookcourse=data["markbookcourse"],
            ownerkey=data["ownerkey"],
            sharelist=data.get("sharelist", []),
            classlist=parse_list(data.get("classlist", []), Class),
            tasklist=parse_list(data.get("tasklist", []), Task),
            studentlist=parse_list(data.get("studentlist", []), StudentWithResults),
        )


@dataclass
class GetMarkbookAltResponse(ApiResponseBase, MarkbookAlt):
    """
    Returned by: ``getmarkbookalt``

    Normalised variant where student results are separated from student
    identity records.
    """

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> GetMarkbookAltResponse:
        return cls(
            **ApiResponseBase._base_kwargs(data),
            markbookkey=data["markbookkey"],
            markbookname=data["markbookname"],
            markbookyear=data["markbookyear"],
            markbookcourse=data["markbookcourse"],
            ownerkey=data["ownerkey"],
            sharelist=data.get("sharelist", []),
            classlist=parse_list(data.get("classlist", []), Class),
            tasklist=parse_list(data.get("tasklist", []), Task),
            studentlist=parse_list(data.get("studentlist", []), StudentBase),
            resultlist=parse_list(data.get("resultlist", []), Result),
        )


@dataclass
class GetOutcomesResponse(ApiResponseBase):
    """Returned by: ``getoutcomes``"""

    classlist: list[Class]
    outcomelist: list[Outcome]
    studentlist: list[StudentWithOutcomes]


@dataclass
class GetOutcomesAltResponse(ApiResponseBase):
    """Returned by: ``getoutcomesalt``"""

    classlist: list[Class]
    outcomelist: list[Outcome]
    studentlist: list[StudentBase]
    levellist: list[OutcomeLevel]


@dataclass
class MarkbookActionResponse(ApiResponseBase):
    """
    Generic response for write actions (create, update, delete).

    Returned by: ``putstudentresult``, ``createstudent``, ``updatestudent``,
    ``updatestudentclass``, ``deletestudent``, ``createclass``,
    ``createmarkbook``, ``schedulebackup``.
    """

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> MarkbookActionResponse:
        return cls(**ApiResponseBase._base_kwargs(data))
