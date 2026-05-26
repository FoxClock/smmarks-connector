"""
smmarks_connector.models.utils
===============================
Shared helpers for deserialising API response payloads.
"""

from __future__ import annotations

from typing import Any, Type, TypeVar

T = TypeVar("T")


def parse_list(data: list[dict[str, Any]], cls: Type[T]) -> list[T]:
    """
    Deserialise a list of raw JSON objects into typed dataclass instances.

    Each item in *data* is passed to ``cls.from_json()``.  The caller is
    responsible for ensuring that *cls* exposes a ``from_json`` class method.

    :param data: List of raw dictionaries from a parsed JSON response.
    :type data: list[dict[str, Any]]
    :param cls: Target dataclass type with a ``from_json`` factory method.
    :type cls: Type[T]
    :return: List of *cls* instances.
    :rtype: list[T]
    """
    return [cls.from_json(item) for item in data]
