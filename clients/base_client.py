import json
import logging
from typing import Any

import allure
import requests

from config.settings import settings

logger = logging.getLogger("autotest.http")


class _TimeoutSession(requests.Session):
    """A Session that applies a default timeout to every request."""

    def __init__(self, timeout: float) -> None:
        super().__init__()
        self._timeout = timeout

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self._timeout)
        return super().request(method, url, **kwargs)


class ApiResponse:
    """A wrapper around requests.Response for the automationexercise API.

    Solves issue that we get 200 response status code even on errors (the real
    status is the responseCode field in the JSON body)
    """

    def __init__(self, response: requests.Response) -> None:
        self.response = response

    @property
    def http_status(self) -> int:
        """Shows http status code, usually 200, only shows that server responded
        but the real request's status code will be in the .response_code"""
        return self.response.status_code

    @property
    def response_code(self) -> int | None:
        """The API's real status code, read from the body."""
        body = self.response.json()
        return body.get("responseCode") if isinstance(body, dict) else None

    @property
    def json(self) -> str:
        """Added in order not to have .response before .json() every time"""
        return self.response.json()

    @property
    def text(self) -> str:
        """Added in order not to have .response before .text every time"""
        return self.response.text


class BaseClient:
    """Base HTTP client. Resource clients wrap an instance of this rather than
    talking to requests directly."""

    def __init__(
        self, base_url: str | None = None, timeout: float | None = None
    ) -> None:
        self.base_url = (base_url or settings.api_url).rstrip("/")
        self.session = _TimeoutSession(timeout or settings.timeout)
        self.session.headers.update({"Accept": "application/json"})
        # Log + attach to Allure for EVERY response on this session.
        self.session.hooks["response"].append(self._log_response)
        logger.setLevel(settings.log_level)

    def _url(self, path: str) -> str:
        """Join a path onto the base URL. Call sites pass only the path."""
        return f"{self.base_url}/{path.lstrip('/')}"

    # --------------------------------------------------------------- logging #
    def _log_response(
        self, response: requests.Response, *args: Any, **kwargs: Any
    ) -> None:
        """requests response-hook: log the request/response line and attach
        both bodies to the Allure report."""
        request = response.request
        logger.info(
            "%s %s -> %s (%.0f ms)",
            request.method,
            request.url,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )
        allure.attach(
            f"{request.method} {request.url}\n\n{_as_text(request.body)}",
            name="request",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            _pretty(response.text),
            name=f"response ({response.status_code})",
            attachment_type=allure.attachment_type.JSON,
        )

    def get(self, path: str, **kwargs: Any) -> ApiResponse:
        """Perform a GET and returns an ApiResponse class."""
        return ApiResponse(self.session.get(self._url(path), **kwargs))

    def post(self, path: str, **kwargs: Any) -> ApiResponse:
        """Perform a POST and returns an ApiResponse class."""
        return ApiResponse(self.session.post(self._url(path), **kwargs))

    def put(self, path: str, **kwargs: Any) -> ApiResponse:
        """Perform a PUT and returns an ApiResponse class."""
        return ApiResponse(self.session.put(self._url(path), **kwargs))

    def delete(self, path: str, **kwargs: Any) -> ApiResponse:
        """Perform a DELETE and returns an ApiResponse class."""
        return ApiResponse(self.session.delete(self._url(path), **kwargs))


# --------------------------------------------------------------------------- #
# Small helpers for the Allure attachments
# --------------------------------------------------------------------------- #
def _as_text(body: Any) -> str:
    """Helpers for the Allure attachments. Renders a request body (bytes/str/None)
    as text for an attachment."""
    if body is None:
        return ""
    if isinstance(body, bytes):
        return body.decode("utf-8", errors="replace")
    return str(body)


def _pretty(text: str) -> str:
    """Best-effort pretty-print of a JSON string, return it as-is otherwise."""
    try:
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except (ValueError, TypeError):
        return text
