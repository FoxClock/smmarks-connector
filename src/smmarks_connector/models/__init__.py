"""smmarks_connector.models — all public model types."""

from .base import ApiResponseBase
from .classes import Class
from .markbooks import Markbook, MarkbookAlt, MarkbookCreate, MarkbookSummary
from .outcomes import Outcome, OutcomeLevel
from .responses import (
    GetMarkbookAltResponse,
    GetMarkbookResponse,
    GetOutcomesAltResponse,
    GetOutcomesResponse,
    MarkbookActionResponse,
    MarkbookListResponse,
    UserListResponse,
)
from .results import Result
from .students import StudentBase, StudentWithOutcomes, StudentWithResults
from .tasks import Task
from .users import AuthenticationResponse, User

__all__ = [
    # Base
    "ApiResponseBase",
    # Primitives
    "Class",
    "Task",
    "Result",
    "Outcome",
    "OutcomeLevel",
    # Students
    "StudentBase",
    "StudentWithResults",
    "StudentWithOutcomes",
    # Users
    "User",
    "AuthenticationResponse",
    # Markbooks
    "MarkbookSummary",
    "Markbook",
    "MarkbookAlt",
    "MarkbookCreate",
    # Responses
    "UserListResponse",
    "MarkbookListResponse",
    "GetMarkbookResponse",
    "GetMarkbookAltResponse",
    "GetOutcomesResponse",
    "GetOutcomesAltResponse",
    "MarkbookActionResponse",
]
