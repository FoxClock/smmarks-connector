"""smmarks_connector.models.outcomes — Outcome and OutcomeLevel dataclasses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Outcome:
    """
    Defines a curriculum learning outcome.

    Returned by: ``getoutcomes``, ``getoutcomesalt``
    """

    key: int
    code: str
    name: str
    outcome: str
    tasklist: list[int]


@dataclass
class OutcomeLevel:
    """
    A student's achievement level against a single outcome.

    Returned by: ``getoutcomesalt``
    """

    studentkey: int
    outcomekey: int
    outcomelevel: str
