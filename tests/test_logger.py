"""Tests for smmarks_connector.logger — scrubbing and configuration."""

from __future__ import annotations

import logging

from smmarks_connector.logger import (
    DEFAULT_REDACT_FIELDS,
    ScrubFilter,
    configure,
    get_logger,
    scrub,
)


class TestGetLogger:
    def test_returns_namespaced_logger(self):
        logger = get_logger("api")
        assert logger.name == "smmarks_connector.api"

    def test_returns_logging_logger_instance(self):
        assert isinstance(get_logger("test"), logging.Logger)

    def test_different_names_produce_different_loggers(self):
        assert get_logger("a") is not get_logger("b")

    def test_same_name_returns_same_instance(self):
        assert get_logger("x") is get_logger("x")


class TestScrub:
    def setup_method(self):
        """Reset to default redact fields before every test."""
        configure()

    def test_redacts_default_sensitive_fields(self):
        data = {"apipassword": "secret", "method": "GET"}
        result = scrub(data)
        assert result["apipassword"] == "[REDACTED]"
        assert result["method"] == "GET"

    def test_all_default_fields_are_redacted(self):
        data = dict.fromkeys(DEFAULT_REDACT_FIELDS, "value")
        result = scrub(data)
        assert all(v == "[REDACTED]" for v in result.values())

    def test_non_sensitive_fields_are_unchanged(self):
        data = {"method": "GET", "url": "https://example.com", "action": "userlist"}
        assert scrub(data) == data

    def test_redacts_nested_sensitive_fields(self):
        data = {"params": {"sessiontoken": "tok123", "action": "userlist"}}
        result = scrub(data)
        assert result["params"]["sessiontoken"] == "[REDACTED]"
        assert result["params"]["action"] == "userlist"

    def test_returns_new_dict_does_not_mutate_input(self):
        data = {"apipassword": "secret"}
        result = scrub(data)
        assert data["apipassword"] == "secret"
        assert result is not data

    def test_empty_dict_returns_empty_dict(self):
        assert scrub({}) == {}


class TestConfigure:
    def teardown_method(self):
        """Always restore defaults after tests that change config."""
        configure()

    def test_configure_none_uses_defaults(self):
        configure(redact_fields=None)
        data = {"apipassword": "s", "apikey": "k"}
        result = scrub(data)
        assert result["apipassword"] == "[REDACTED]"
        assert result["apikey"] == "[REDACTED]"

    def test_configure_custom_fields_overrides_defaults(self):
        configure(redact_fields=["mypassword"])
        data = {"mypassword": "secret", "apipassword": "also_secret"}
        result = scrub(data)
        assert result["mypassword"] == "[REDACTED]"
        # apipassword is NOT in the custom list
        assert result["apipassword"] == "also_secret"

    def test_configure_empty_list_disables_all_redaction(self):
        configure(redact_fields=[])
        data = {"apipassword": "secret", "sessiontoken": "tok"}
        result = scrub(data)
        assert result["apipassword"] == "secret"
        assert result["sessiontoken"] == "tok"

    def test_configure_is_case_insensitive(self):
        configure(redact_fields=["MyPassword"])
        data = {"mypassword": "secret"}
        assert scrub(data)["mypassword"] == "[REDACTED]"


class TestScrubFilter:
    def test_redacts_data_attribute_on_record(self):
        f = ScrubFilter(DEFAULT_REDACT_FIELDS)
        record = logging.LogRecord("test", logging.DEBUG, "", 0, "", (), None)
        record.data = {"apikey": "secret", "action": "userlist"}
        f.filter(record)
        assert record.data["apikey"] == "[REDACTED]"
        assert record.data["action"] == "userlist"

    def test_filter_always_returns_true(self):
        f = ScrubFilter(DEFAULT_REDACT_FIELDS)
        record = logging.LogRecord("test", logging.DEBUG, "", 0, "", (), None)
        assert f.filter(record) is True

    def test_filter_with_no_data_attribute_does_not_raise(self):
        f = ScrubFilter(DEFAULT_REDACT_FIELDS)
        record = logging.LogRecord("test", logging.DEBUG, "", 0, "", (), None)
        assert f.filter(record) is True

    def test_filter_with_empty_redact_fields_leaves_record_unchanged(self):
        f = ScrubFilter(frozenset())
        record = logging.LogRecord("test", logging.DEBUG, "", 0, "", (), None)
        record.data = {"apipassword": "secret"}
        f.filter(record)
        assert record.data["apipassword"] == "secret"
