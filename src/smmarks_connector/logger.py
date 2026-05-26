"""
smmarks_connector.logger
========================
Logging utilities for the smmarks_connector package.

Design principles
-----------------
* **No handlers are attached here.** Attaching handlers in library code
  pollutes the consuming application's logging configuration. The application
  is responsible for adding handlers, setting levels, and choosing formatters.
  A single :class:`logging.NullHandler` is added at the package root so that
  "No handlers could be found" warnings are suppressed when the application
  has not configured logging at all.

* **Redaction is opt-in and application-controlled.** Sensitive field values
  are replaced with ``[REDACTED]`` only after the application calls
  :func:`smmarks_connector.configure`. The default sensitive field set covers
  the known authentication parameters of the SM Marks API, but can be
  fully overridden or disabled.

* **Scrubbing happens at the call site**, before the value reaches any
  handler or formatter. :class:`ScrubFilter` is provided as an additional
  defence-in-depth layer for applications that want handler-level enforcement.

Usage
-----
Application startup (recommended pattern)::

    import logging
    from smmarks_connector import configure

    configure()                         # activates default redaction
    logging.basicConfig(level=logging.DEBUG)

Custom redact fields::

    configure(redact_fields=["mypassword", "mytoken"])

Disable redaction entirely::

    configure(redact_fields=[])
"""

from __future__ import annotations

import logging
from typing import Any

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

#: Fields redacted by default when :func:`configure` is called with
#: ``redact_fields=None``.
DEFAULT_REDACT_FIELDS: frozenset[str] = frozenset(
    {
        "apiuser",
        "apipassword",
        "sessiontoken",
        "sessionkey",
        "apikey",
    }
)

_REDACTED_PLACEHOLDER = "[REDACTED]"

# ---------------------------------------------------------------------------
# Package root — NullHandler only (PEP 3110 / logging HOWTO for libraries)
# ---------------------------------------------------------------------------
logging.getLogger("smmarks_connector").addHandler(logging.NullHandler())

# ---------------------------------------------------------------------------
# Module-level redaction state
# Mutated exclusively by configure(); read by scrub().
# ---------------------------------------------------------------------------
_active_redact_fields: frozenset[str] = frozenset()  # empty until configure() is called


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def configure(redact_fields: list[str] | None = None) -> None:
    """
    Configure smmarks_connector log-redaction behaviour.

    Call this **once at application startup**, before any API calls are made.
    Calling it again replaces the active field set.

    :param redact_fields:
        List of field names whose values will be replaced with
        ``"[REDACTED]"`` in all structured log output produced by this
        library.

        * Pass ``None`` (the default) to activate the built-in sensitive
          field set: ``apiuser``, ``apipassword``, ``sessiontoken``,
          ``sessionkey``, ``apikey``.
        * Pass a custom list to override the defaults entirely.
        * Pass an empty list ``[]`` to disable redaction.

    :type redact_fields: list[str] | None

    Example::

        from smmarks_connector import configure

        # Built-in defaults
        configure()

        # Custom fields
        configure(redact_fields=["mypassword", "bearer_token"])

        # No redaction
        configure(redact_fields=[])
    """
    global _active_redact_fields
    if redact_fields is None:
        _active_redact_fields = DEFAULT_REDACT_FIELDS
    else:
        _active_redact_fields = frozenset(f.lower() for f in redact_fields)


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger namespaced under ``smmarks_connector``.

    All internal loggers are created through this factory so that the
    consuming application can control them via the ``smmarks_connector``
    logger hierarchy.

    :param name: Sub-logger name (e.g. ``"api"``, ``"auth"``).
    :type name: str
    :return: A :class:`logging.Logger` instance.
    :rtype: logging.Logger
    """
    return logging.getLogger(f"smmarks_connector.{name}")


def scrub(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a copy of *data* with sensitive field values replaced.

    Redaction is applied according to the field set most recently set by
    :func:`configure`. If :func:`configure` has not been called, no fields
    are redacted (the active set is empty by default).

    Scrubbing is **recursive** — nested dicts are processed depth-first.
    Non-dict values are passed through unchanged.

    :param data: Dictionary that may contain sensitive values.
    :type data: dict[str, Any]
    :return: New dictionary safe for inclusion in log records.
    :rtype: dict[str, Any]
    """
    return _scrub_dict(data, _active_redact_fields)


# ---------------------------------------------------------------------------
# ScrubFilter — handler-level defence in depth
# ---------------------------------------------------------------------------


class ScrubFilter(logging.Filter):
    """
    A :class:`logging.Filter` that redacts sensitive key/value pairs from
    structured log records emitted by this library.

    The library already calls :func:`scrub` before populating log records, so
    attaching this filter is optional. It is provided for applications that
    want a second layer of protection at the handler level — for example, when
    log records might be forwarded to an external log aggregator.

    :param redact_fields: Set of lowercase field names to redact.
    :type redact_fields: frozenset[str]

    Example::

        import logging
        from smmarks_connector.logger import ScrubFilter, DEFAULT_REDACT_FIELDS

        handler = logging.StreamHandler()
        handler.addFilter(ScrubFilter(DEFAULT_REDACT_FIELDS))
        logging.getLogger("smmarks_connector").addHandler(handler)
    """

    def __init__(self, redact_fields: frozenset[str]) -> None:
        super().__init__()
        self._redact_fields = redact_fields

    def filter(self, record: logging.LogRecord) -> bool:
        """Scrub the ``data`` attribute of *record* in place, if present."""
        if hasattr(record, "data") and isinstance(record.data, dict):
            record.data = _scrub_dict(record.data, self._redact_fields)
        return True


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _scrub_dict(data: dict[str, Any], fields: frozenset[str]) -> dict[str, Any]:
    """Recursively replace values whose keys are in *fields*."""
    result: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in fields:
            result[key] = _REDACTED_PLACEHOLDER
        elif isinstance(value, dict):
            result[key] = _scrub_dict(value, fields)
        else:
            result[key] = value
    return result
