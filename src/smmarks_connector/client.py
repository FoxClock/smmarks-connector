"""
smmarks_connector.client
=========================
High-level facade for all SM Marks (Markbook Online) API actions.

Typical usage::

    from smmarks_connector import MarkbookApiClient, InitialAuthStrategy, configure

    configure()                 # enable log redaction (optional)

    client = MarkbookApiClient(
        baseUrl="https://marks.school.edu.au",
        authStrat=InitialAuthStrategy("username", "password"),
        api_key="your-api-key",
    )
    client.authenticate()
    summary = client.get_markbook_summary()
"""

from __future__ import annotations

import json
from dataclasses import asdict
from enum import Enum
from functools import wraps
from typing import Any

from .auth.base import AuthStrategy
from .auth.strategy import OngoingAuthStrategy
from .base import ApiBase
from .models.markbooks import MarkbookCreate
from .models.responses import (
    GetMarkbookResponse,
    MarkbookActionResponse,
    MarkbookListResponse,
    UserListResponse,
)

# ---------------------------------------------------------------------------
# Action enum
# ---------------------------------------------------------------------------


class APIAction(Enum):
    """Enumeration of all known SM Marks API action strings."""

    markbookList = "markbooklist"
    userList = "userlist"
    getMarkbook = "getmarkbook"
    getMarkbookAlt = "getmarkbookalt"
    getOutcomes = "getoutcomes"
    getOutcomesAlt = "getoutcomesalt"
    putStudentResult = "putstudentresult"
    createStudent = "createstudent"
    updateStudent = "updatestudent"
    updateStudentClass = "updatestudentclass"
    deleteStudent = "deletestudent"
    createClass = "createclass"
    scheduleBackup = "schedulebackup"
    getBackupURL = "getbackupurl"
    createMarkbook = "createmarkbook"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class MarkbookApiClient(ApiBase):
    """
    Authenticated client for the SM Marks (Markbook Online) API.

    All methods require the client to be authenticated first — call
    :meth:`authenticate` before any other method.

    :param baseUrl: Root URL of the SM Marks instance.
    :type baseUrl: str
    :param authStrat: Initial authentication strategy (typically
        :class:`~smmarks_connector.auth.strategy.InitialAuthStrategy`).
    :type authStrat: AuthStrategy
    :param api_key: Static API key issued to this integration.
    :type api_key: str
    :raises ValueError: If *api_key* is empty or falsy.
    """

    SUCCESS = "OKAY"

    # ------------------------------------------------------------------
    # Authentication guard decorator
    # ------------------------------------------------------------------

    @staticmethod
    def checkAuthenticated(func):  # noqa: N802
        """Raise :exc:`ConnectionError` if the client is not authenticated."""

        @wraps(func)
        def _decorator(self, *args, **kwargs):
            if self.is_authenticated:
                return func(self, *args, **kwargs)
            raise ConnectionError("SM Marks is not authenticated. Call authenticate() first.")

        return _decorator

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(self, baseUrl: str, authStrat: AuthStrategy, api_key: str) -> None:
        super().__init__(baseUrl, authStrat)

        if not api_key:
            raise ValueError("API Key is required to interact with the API. None was provided.")

        self.api_key: str = api_key
        self.is_authenticated: bool = False

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> None:
        """
        Perform the initial authentication handshake with SM Marks.

        On success the client swaps its auth strategy to
        :class:`~smmarks_connector.auth.strategy.OngoingAuthStrategy` and
        sets :attr:`is_authenticated` to ``True``.  All subsequent requests
        use the returned session token and key.

        :raises ConnectionRefusedError: If the server rejects the credentials.
        :raises ConnectionError: If the response is missing the session token
            or key.
        """
        response = self.request("POST", "authenticate.lc", data=self.authStrategy.get_auth_params())

        if response.get("status") != self.SUCCESS:
            raise ConnectionRefusedError(
                "Unable to authenticate with SM Marks. Check username or password."
            )

        token = response.get("sessiontoken")
        key = response.get("sessionkey")

        if not token or not key:
            raise ConnectionError("Invalid authentication response: session token or key missing.")

        self.authStrategy = OngoingAuthStrategy(token, key, self.api_key)
        self.is_authenticated = True

    # ------------------------------------------------------------------
    # Read actions
    # ------------------------------------------------------------------

    @checkAuthenticated
    def get_users(self) -> UserListResponse:
        """
        Return a list of all users registered in the SM Marks instance.

        :return: Parsed user list response.
        :rtype: UserListResponse
        """
        response = self.request("GET", "", params={"action": APIAction.userList.value})
        return UserListResponse.from_json(response)

    @checkAuthenticated
    def get_markbook_summary(self) -> MarkbookListResponse:
        """
        Return a lightweight summary of all markbooks accessible to the
        authenticated user.

        :return: Parsed markbook list response.
        :rtype: MarkbookListResponse
        """
        response = self.request("GET", "", params={"action": APIAction.markbookList.value})
        return MarkbookListResponse.from_json(response)

    @checkAuthenticated
    def get_markbook(self, key: int) -> GetMarkbookResponse:
        """
        Return the full contents of a single markbook.

        :param key: Primary key of the markbook to retrieve.
        :type key: int
        :return: Parsed markbook response including classes, tasks, and
            students with their results.
        :rtype: GetMarkbookResponse
        """
        response = self.request(
            "GET", "", params={"action": APIAction.getMarkbook.value, "key": key}
        )
        return GetMarkbookResponse.from_json(response)

    # ------------------------------------------------------------------
    # Student result actions
    # ------------------------------------------------------------------

    @checkAuthenticated
    def put_student_result(
        self,
        key: int,
        studentkey: int,
        studentid: str,
        taskkey: int,
        taskname: str,
        result: str,
    ) -> MarkbookActionResponse:
        """
        Insert or overwrite a student's result for a specific task.

        :param key: Markbook primary key.
        :type key: int
        :param studentkey: Student primary key within the markbook.
        :type studentkey: int
        :param studentid: Student's school ID string.
        :type studentid: str
        :param taskkey: Task primary key within the markbook.
        :type taskkey: int
        :param taskname: Task name (must match the markbook task).
        :type taskname: str
        :param result: Result value to write (numeric or string).
        :type result: str
        :return: Action response indicating success or failure.
        :rtype: MarkbookActionResponse
        :raises ValueError: If any key argument is not an integer.
        """
        if not (isinstance(key, int) and isinstance(studentkey, int) and isinstance(taskkey, int)):
            raise ValueError("Keys must always be of integer type: (key, studentkey, taskkey).")

        params: dict[str, Any] = {
            "action": APIAction.putStudentResult.value,
            "key": key,
            "studentkey": studentkey,
            "studentid": studentid,
            "taskkey": taskkey,
            "taskname": taskname,
            "result": result,
        }
        response = self.request("GET", "", params=params)
        return MarkbookActionResponse.from_json(response)

    # ------------------------------------------------------------------
    # Student management actions
    # ------------------------------------------------------------------

    @checkAuthenticated
    def create_student(
        self,
        key: int,
        studentId: str,
        familyName: str,
        givenName: str,
        classKey: int,
        gender: str = "M",
        preferredName: str = "",
    ) -> MarkbookActionResponse:
        """
        Create a new student record in an existing markbook.

        The ``studentId`` must be unique within the markbook, and
        ``classKey`` must reference an existing class.

        :param key: Markbook primary key.
        :type key: int
        :param studentId: Unique student school ID.
        :type studentId: str
        :param familyName: Student family name.
        :type familyName: str
        :param givenName: Student given name.
        :type givenName: str
        :param classKey: Primary key of the class to assign the student to.
        :type classKey: int
        :param gender: Student gender code (default ``"M"``).
        :type gender: str
        :param preferredName: Student preferred name (optional).
        :type preferredName: str
        :return: Action response.
        :rtype: MarkbookActionResponse
        :raises ValueError: If any required argument is falsy.
        """
        if not all([key, studentId, familyName, givenName, classKey]):
            raise ValueError("create_student is missing a required value.")

        params: dict[str, Any] = {
            "action": APIAction.createStudent.value,
            "key": key,
            "sid": studentId,
            "family": familyName,
            "given": givenName,
            "preffered": preferredName,
            "gender": gender,
            "classkey": classKey,
        }
        response = self.request("GET", "", params=params)
        return MarkbookActionResponse.from_json(response)

    @checkAuthenticated
    def update_student(
        self,
        key: int,
        studentkey: int,
        studentId: str,
        familyName: str,
        givenName: str,
        gender: str = "Male",
        prefferedName: str = "",
    ) -> MarkbookActionResponse:
        """
        Update an existing student's details.

        :param key: Markbook primary key.
        :type key: int
        :param studentkey: Student primary key.
        :type studentkey: int
        :param studentId: Student school ID.
        :type studentId: str
        :param familyName: Updated family name.
        :type familyName: str
        :param givenName: Updated given name.
        :type givenName: str
        :param gender: Updated gender (default ``"Male"``).
        :type gender: str
        :param prefferedName: Updated preferred name.
        :type prefferedName: str
        :return: Action response.
        :rtype: MarkbookActionResponse
        :raises ValueError: If any required argument is falsy.
        """
        if not all([key, studentkey, studentId, familyName, givenName]):
            raise ValueError("update_student is missing a required value.")

        params: dict[str, Any] = {
            "action": APIAction.updateStudent.value,
            "key": key,
            "studentkey": studentkey,
            "sid": studentId,
            "family": familyName,
            "given": givenName,
            "preferred": prefferedName,
            "gender": gender,
        }
        response = self.request("GET", "", params=params)
        return MarkbookActionResponse.from_json(response)

    @checkAuthenticated
    def update_student_class(
        self, key: int, studentKey: int, studentId: str, classkey: int
    ) -> MarkbookActionResponse:
        """
        Move a student to a different class within the same markbook.

        :param key: Markbook primary key.
        :type key: int
        :param studentKey: Student primary key.
        :type studentKey: int
        :param studentId: Student school ID.
        :type studentId: str
        :param classkey: Primary key of the destination class.
        :type classkey: int
        :return: Action response.
        :rtype: MarkbookActionResponse
        :raises TypeError: If *key*, *studentKey*, or *classkey* are not
            all integers.
        """
        if not all(isinstance(p, int) for p in (key, studentKey, classkey)):
            raise TypeError("key, studentKey, and classkey must all be integers.")

        params: dict[str, Any] = {
            "action": APIAction.updateStudentClass.value,
            "key": key,
            "studentkey": studentKey,
            "sid": studentId,
            "classkey": classkey,
        }
        response = self.request("GET", "", params=params)
        return MarkbookActionResponse.from_json(response)

    @checkAuthenticated
    def delete_student(self, key: int, studentKey: int, studentId: str) -> MarkbookActionResponse:
        """
        Permanently remove a student from a markbook.

        :param key: Markbook primary key.
        :type key: int
        :param studentKey: Student primary key.
        :type studentKey: int
        :param studentId: Student school ID.
        :type studentId: str
        :return: Action response.
        :rtype: MarkbookActionResponse
        :raises TypeError: If *key* or *studentKey* are not integers.
        """
        if not all(isinstance(p, int) for p in (key, studentKey)):
            raise TypeError("key and studentKey must be integers.")

        params: dict[str, Any] = {
            "action": APIAction.deleteStudent.value,
            "key": key,
            "studentkey": studentKey,
            "sid": studentId,
        }
        response = self.request("GET", "", params=params)
        return MarkbookActionResponse.from_json(response)

    # ------------------------------------------------------------------
    # Class management actions
    # ------------------------------------------------------------------

    @checkAuthenticated
    def create_class(self, key: int, name: str, family: str, given: str) -> MarkbookActionResponse:
        """
        Create a new class within an existing markbook.

        :param key: Markbook primary key.
        :type key: int
        :param name: Class name (e.g. ``"10A"``).
        :type name: str
        :param family: Teacher's family name.
        :type family: str
        :param given: Teacher's given name.
        :type given: str
        :return: Action response.
        :rtype: MarkbookActionResponse
        """
        params: dict[str, Any] = {
            "action": APIAction.createClass.value,
            "key": key,
            "name": name,
            "family": family,
            "given": given,
        }
        response = self.request("GET", "", params=params)
        return MarkbookActionResponse.from_json(response)

    # ------------------------------------------------------------------
    # Markbook management actions
    # ------------------------------------------------------------------

    @checkAuthenticated
    def create_markbook(self, markbook: MarkbookCreate) -> MarkbookActionResponse:
        """
        Create a new markbook via the POST endpoint.

        The markbook payload is serialised to compact JSON and sent as the
        ``jsondata`` form field.  Auth parameters are embedded in the POST
        body because ``post.lc`` does not read query-string auth.

        :param markbook: Fully populated markbook creation payload.
        :type markbook: MarkbookCreate
        :return: Action response.
        :rtype: MarkbookActionResponse
        """
        # post.lc uses "apiaction" (not "action") and expects all params —
        # including auth — in the POST body, not the query string.
        # Compact JSON (no whitespace) reduces payload size.
        form_data: dict[str, str] = {
            "apiaction": APIAction.createMarkbook.value,
            "jsondata": json.dumps(asdict(markbook), separators=(",", ":")),
        }
        form_data.update(self.authStrategy.get_auth_params())

        response = self.request("POST", "post.lc", data=form_data)
        return MarkbookActionResponse.from_json(response)
