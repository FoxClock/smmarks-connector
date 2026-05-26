"""Tests for MarkbookApiClient — auth guard, init validation, authenticate()."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from smmarks_connector import InitialAuthStrategy, MarkbookApiClient
from smmarks_connector.auth.strategy import OngoingAuthStrategy


def _make_client(api_key: str = "test-api-key") -> MarkbookApiClient:
    """Return a fresh, unauthenticated client."""
    return MarkbookApiClient(
        baseUrl="https://marks.example.com",
        authStrat=InitialAuthStrategy("user", "pass"),
        api_key=api_key,
    )


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestMarkbookApiClientInit:
    def test_raises_value_error_when_api_key_is_empty_string(self):
        with pytest.raises(ValueError, match="API Key is required"):
            _make_client(api_key="")

    def test_raises_value_error_when_api_key_is_none(self):
        with pytest.raises(ValueError, match="API Key is required"):
            MarkbookApiClient(
                baseUrl="https://marks.example.com",
                authStrat=InitialAuthStrategy("u", "p"),
                api_key=None,
            )

    def test_is_authenticated_is_false_on_init(self):
        client = _make_client()
        assert client.is_authenticated is False

    def test_api_key_stored(self):
        client = _make_client(api_key="my-key")
        assert client.api_key == "my-key"


# ---------------------------------------------------------------------------
# checkAuthenticated decorator
# ---------------------------------------------------------------------------


class TestCheckAuthenticated:
    def test_get_users_raises_when_not_authenticated(self):
        client = _make_client()
        with pytest.raises(ConnectionError, match="not authenticated"):
            client.get_users()

    def test_get_markbook_summary_raises_when_not_authenticated(self):
        client = _make_client()
        with pytest.raises(ConnectionError):
            client.get_markbook_summary()

    def test_get_markbook_raises_when_not_authenticated(self):
        client = _make_client()
        with pytest.raises(ConnectionError):
            client.get_markbook(key=1)


# ---------------------------------------------------------------------------
# authenticate()
# ---------------------------------------------------------------------------


class TestAuthenticate:
    def test_success_sets_is_authenticated(self):
        client = _make_client()
        mock_response = {"status": "OKAY", "sessiontoken": "tok123", "sessionkey": 42}
        with patch.object(client, "request", return_value=mock_response):
            client.authenticate()
        assert client.is_authenticated is True

    def test_success_swaps_auth_strategy_to_ongoing(self):
        client = _make_client()
        mock_response = {"status": "OKAY", "sessiontoken": "tok", "sessionkey": 99}
        with patch.object(client, "request", return_value=mock_response):
            client.authenticate()
        assert isinstance(client.authStrategy, OngoingAuthStrategy)

    def test_ongoing_strategy_carries_correct_values(self):
        client = _make_client(api_key="mykey")
        mock_response = {"status": "OKAY", "sessiontoken": "mytok", "sessionkey": 7}
        with patch.object(client, "request", return_value=mock_response):
            client.authenticate()
        strat = client.authStrategy
        assert strat.token == "mytok"
        assert strat.key == 7
        assert strat.apikey == "mykey"

    def test_bad_status_raises_connection_refused_error(self):
        client = _make_client()
        with patch.object(client, "request", return_value={"status": "ERROR"}), \
            pytest.raises(ConnectionRefusedError):
                client.authenticate()

    def test_missing_token_raises_connection_error(self):
        client = _make_client()
        mock = {"status": "OKAY", "sessiontoken": None, "sessionkey": None}
        with patch.object(client, "request", return_value=mock), pytest.raises(ConnectionError):
                client.authenticate()

    def test_missing_key_raises_connection_error(self):
        client = _make_client()
        mock = {"status": "OKAY", "sessiontoken": "tok", "sessionkey": None}
        with patch.object(client, "request", return_value=mock), pytest.raises(ConnectionError):
                client.authenticate()


# ---------------------------------------------------------------------------
# Argument validation on write methods
# ---------------------------------------------------------------------------


class TestArgumentValidation:
    def setup_method(self):
        """Authenticate the client so validation tests can reach the guard."""
        self.client = _make_client()
        mock_response = {"status": "OKAY", "sessiontoken": "t", "sessionkey": 1}
        with patch.object(self.client, "request", return_value=mock_response):
            self.client.authenticate()

    def test_put_student_result_raises_on_non_int_key(self):
        with pytest.raises(ValueError, match="integer"):
            self.client.put_student_result(
                key="not-an-int",
                studentkey=1,
                studentid="S1",
                taskkey=1,
                taskname="Task",
                result="85",
            )

    def test_update_student_class_raises_on_non_int_params(self):
        with pytest.raises(TypeError):
            self.client.update_student_class(key="x", studentKey=1, studentId="S1", classkey=1)

    def test_delete_student_raises_on_non_int_keys(self):
        with pytest.raises(TypeError):
            self.client.delete_student(key="x", studentKey=1, studentId="S1")
