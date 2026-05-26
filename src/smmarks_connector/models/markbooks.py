"""smmarks_connector.models.markbooks — markbook dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .classes import Class
from .results import Result
from .students import StudentBase, StudentWithResults
from .tasks import Task


@dataclass
class MarkbookSummary:
    """
    Lightweight markbook entry used in list views.

    Returned by: ``markbooklist``
    """

    key: int
    name: str
    owner: str
    year: str
    course: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> MarkbookSummary:
        return cls(
            key=data.get("key"),
            name=data.get("name"),
            owner=data.get("owner"),
            year=data.get("year"),
            course=data.get("course"),
        )


@dataclass
class Markbook:
    """
    Full markbook structure including classes, tasks, and students.

    Returned by: ``getmarkbook``
    """

    markbookkey: int
    markbookname: str
    markbookyear: str
    markbookcourse: str
    ownerkey: int
    sharelist: list[int]
    classlist: list[Class]
    tasklist: list[Task]
    studentlist: list[StudentWithResults]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Markbook:
        return cls(
            markbookkey=data["markbookkey"],
            markbookname=data["markbookname"],
            markbookyear=data["markbookyear"],
            markbookcourse=data["markbookcourse"],
            ownerkey=data["ownerkey"],
            sharelist=data.get("sharelist", []),
            classlist=[Class.from_json(c) for c in data.get("classlist", [])],
            tasklist=[Task.from_json(t) for t in data.get("tasklist", [])],
            studentlist=[StudentWithResults.from_json(s) for s in data.get("studentlist", [])],
        )


@dataclass
class MarkbookAlt:
    """
    Normalised markbook structure with a separate result list.

    Returned by: ``getmarkbookalt``
    """

    markbookkey: int
    markbookname: str
    markbookyear: str
    markbookcourse: str
    ownerkey: int
    sharelist: list[int]
    classlist: list[Class]
    tasklist: list[Task]
    studentlist: list[StudentBase]
    resultlist: list[Result]


@dataclass
class MarkbookCreate:
    """
    Payload for creating a new markbook via ``POST /post.lc``.

    All fields are serialised to compact JSON and sent as the ``jsondata``
    form parameter.  See
    :meth:`~smmarks_connector.client.MarkbookApiClient.create_markbook`.
    """

    api: str
    schoolname: str
    action: str
    markbookname: str
    markbookyear: str
    markbookcourse: str
    ownerkey: int
    sharelist: list[int]
    classlist: list[Class]
    studentlist: list[StudentBase]
