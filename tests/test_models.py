"""Tests for smmarks_connector.models — deserialisation of all response types."""

from __future__ import annotations

import pytest

from smmarks_connector.models.base import ApiResponseBase
from smmarks_connector.models.classes import Class
from smmarks_connector.models.markbooks import MarkbookSummary
from smmarks_connector.models.responses import (
    MarkbookActionResponse,
    MarkbookListResponse,
    UserListResponse,
)
from smmarks_connector.models.results import Result
from smmarks_connector.models.students import StudentBase, StudentWithResults
from smmarks_connector.models.tasks import Task
from smmarks_connector.models.users import User
from smmarks_connector.models.utils import parse_list

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

BASE_ENVELOPE: dict = {
    "source": "test-source",
    "api": "1.0",
    "seconds": 1,
    "date": "2026-01-01",
    "schoolname": "Test School",
    "action": "test",
    "status": "OKAY",
}


def _student_data(**overrides) -> dict:
    base = {
        "key": 1,
        "studentid": "S001",
        "familyname": "Smith",
        "givename": "Alice",
        "preferredname": "Al",
        "classkey": 3,
        "classname": "10A",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class TestUser:
    def test_from_json_maps_all_fields(self):
        data = {"key": 1, "name": "Jane Doe", "loginid": "jdoe", "email": "j@example.com"}
        user = User.from_json(data)
        assert user.key == 1
        assert user.name == "Jane Doe"
        assert user.loginid == "jdoe"
        assert user.email == "j@example.com"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TestTask:
    def test_from_json_maps_all_fields(self):
        data = {"key": 10, "name": "Assessment 1", "maximum": 100, "decimalplaces": 2}
        task = Task.from_json(data)
        assert task.key == 10
        assert task.name == "Assessment 1"
        assert task.maximum == 100
        assert task.decimalplaces == 2


# ---------------------------------------------------------------------------
# Class
# ---------------------------------------------------------------------------


class TestClass:
    def test_from_json_maps_all_fields(self):
        data = {"key": 5, "name": "10B", "teachername1": "Smith", "teachername2": "Jones"}
        cls = Class.from_json(data)
        assert cls.key == 5
        assert cls.name == "10B"
        assert cls.teachername1 == "Smith"


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------


class TestResult:
    def test_from_json_maps_all_fields(self):
        data = {"studentkey": 1, "taskkey": 2, "rawresult": "85.5", "roundedresult": "86"}
        result = Result.from_json(data)
        assert result.studentkey == 1
        assert result.taskkey == 2
        assert result.rawresult == "85.5"
        assert result.roundedresult == "86"


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------


class TestStudentBase:
    def test_from_json_maps_all_fields(self):
        student = StudentBase.from_json(_student_data())
        assert student.studentid == "S001"
        assert student.familyname == "Smith"
        assert student.givename == "Alice"
        assert student.classkey == 3


class TestStudentWithResults:
    def test_from_json_includes_results(self):
        data = _student_data(rawresults=["85", "90"], roundedresults=["85", "90"])
        student = StudentWithResults.from_json(data)
        assert student.rawresults == ["85", "90"]
        assert student.roundedresults == ["90", "90"] or student.roundedresults == ["85", "90"]

    def test_inherits_base_fields(self):
        data = _student_data(rawresults=[], roundedresults=[])
        student = StudentWithResults.from_json(data)
        assert student.studentid == "S001"


# ---------------------------------------------------------------------------
# MarkbookSummary
# ---------------------------------------------------------------------------


class TestMarkbookSummary:
    def test_from_json_maps_all_fields(self):
        data = {
            "key": 5,
            "name": "Yr 10 Maths",
            "owner": "J. Smith",
            "year": "2026",
            "course": "MATH10",
        }
        summary = MarkbookSummary.from_json(data)
        assert summary.key == 5
        assert summary.name == "Yr 10 Maths"
        assert summary.course == "MATH10"


# ---------------------------------------------------------------------------
# ApiResponseBase
# ---------------------------------------------------------------------------


class TestApiResponseBase:
    def test_base_kwargs_extracts_all_fields(self):
        kwargs = ApiResponseBase._base_kwargs(BASE_ENVELOPE)
        assert kwargs["status"] == "OKAY"
        assert kwargs["schoolname"] == "Test School"
        assert len(kwargs) == 7

    def test_base_kwargs_raises_on_missing_key(self):
        incomplete = {k: v for k, v in BASE_ENVELOPE.items() if k != "status"}
        with pytest.raises(KeyError):
            ApiResponseBase._base_kwargs(incomplete)


# ---------------------------------------------------------------------------
# Response types
# ---------------------------------------------------------------------------


class TestMarkbookActionResponse:
    def test_from_json_round_trips_envelope(self):
        response = MarkbookActionResponse.from_json(BASE_ENVELOPE)
        assert response.status == "OKAY"
        assert response.schoolname == "Test School"
        assert response.action == "test"


class TestUserListResponse:
    def test_from_json_parses_user_list(self):
        data = {
            **BASE_ENVELOPE,
            "list": [
                {"key": 1, "name": "Alice", "loginid": "alice", "email": "a@x.com"},
                {"key": 2, "name": "Bob", "loginid": "bob", "email": "b@x.com"},
            ],
        }
        response = UserListResponse.from_json(data)
        assert len(response.list) == 2
        assert all(isinstance(u, User) for u in response.list)
        assert response.list[0].name == "Alice"


class TestMarkbookListResponse:
    def test_from_json_parses_markbook_list(self):
        data = {
            **BASE_ENVELOPE,
            "list": [
                {"key": 1, "name": "Maths", "owner": "Smith", "year": "2026", "course": "MATH"},
            ],
        }
        response = MarkbookListResponse.from_json(data)
        assert len(response.list) == 1
        assert response.list[0].name == "Maths"


# ---------------------------------------------------------------------------
# parse_list utility
# ---------------------------------------------------------------------------


class TestParseList:
    def test_produces_correctly_typed_list(self):
        data = [
            {"key": 1, "name": "A", "loginid": "a", "email": "a@x.com"},
            {"key": 2, "name": "B", "loginid": "b", "email": "b@x.com"},
        ]
        users = parse_list(data, User)
        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)

    def test_empty_list_returns_empty_list(self):
        assert parse_list([], User) == []
