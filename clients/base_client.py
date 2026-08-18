import json
import logging
import time
from typing import Any

import allure
import requests

from config.settings import settings

logger = logging.getLogger("autotest.http")

"""
Retry policy. Transport errors (requests.ConnectionError, requests.Timeout) 
and 5xx are always retried Body-level error codes are only retried when retry_until_ok=True
(positive operations that expect success), negative tests keep the default and get 
their error back on the first try, unmasked.
"""
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 0.5
_TRANSIENT_CODES = frozenset({500, 502, 503, 504})  # immutable set


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
    def status_code(self) -> int | None:
        """The API's real status code, read from the body."""
        return _response_code(self.response)

    @property
    def json(self) -> dict:
        """Added in order not to have .response before .json() every time"""
        return self.response.json()

    @property
    def text(self) -> str:
        """Added in order not to have .response before .text every time"""
        return self.response.text


class BaseClient:
    """Base HTTP client. Resource clients wrap an instance of this rather than
    talking to requests directly."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
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
    def _log_response(self, response: requests.Response, *args: Any, **kwargs: Any) -> None:
        """requests response-hook: log the request/response line and attach
        both bodies to the Allure report."""
        request = response.request
        code = _response_code(response)
        # HTTP status is uselessly always 200 here; the responseCode is the real
        # status, so an error code logs at WARNING to stand out in the trace.
        level = logging.INFO if (code or 0) < 400 else logging.WARNING
        logger.log(
            level,
            "%s %s -> HTTP %s responseCode=%s (%.0f ms)",
            request.method,
            request.url,
            response.status_code,
            code,
            response.elapsed.total_seconds() * 1000,
        )
        if request.body:
            logger.log(level, "  request body: %s", _as_text(request.body))
        message = _response_message(response)
        if message is not None:
            logger.log(level, "  response message: %s", message)
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

    def _request(
        self, method: str, path: str, *, retry_until_ok: bool = False, **kwargs: Any
    ) -> ApiResponse:
        """Send a request, retry failures (_TRANSIENT_CODES and retry_until_ok)."""
        url = self._url(path)
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            last = attempt == _MAX_ATTEMPTS
            try:
                response = self.session.request(method, url, **kwargs)
            except (requests.ConnectionError, requests.Timeout):
                if last:
                    raise  # exit with ConnectionError/Timeout
                logger.warning(
                    "  retrying %s %s after transport error (attempt %d/%d)",
                    method,
                    url,
                    attempt + 1,
                    _MAX_ATTEMPTS,
                )
            else:
                if last or not _should_retry(response, retry_until_ok):
                    return ApiResponse(response)
                logger.warning(
                    "  retrying %s %s, responseCode=%s (attempt %d/%d)",
                    method,
                    url,
                    _response_code(response),
                    attempt + 1,
                    _MAX_ATTEMPTS,
                )
            time.sleep(_BACKOFF_SECONDS * attempt)

    def get(self, path: str, *, retry_until_ok: bool = False, **kwargs: Any) -> ApiResponse:
        """Perform a GET and return an ApiResponse."""
        return self._request("GET", path, retry_until_ok=retry_until_ok, **kwargs)

    def post(self, path: str, *, retry_until_ok: bool = False, **kwargs: Any) -> ApiResponse:
        """Perform a POST and return an ApiResponse."""
        return self._request("POST", path, retry_until_ok=retry_until_ok, **kwargs)

    def put(self, path: str, *, retry_until_ok: bool = False, **kwargs: Any) -> ApiResponse:
        """Perform a PUT and return an ApiResponse."""
        return self._request("PUT", path, retry_until_ok=retry_until_ok, **kwargs)

    def delete(self, path: str, *, retry_until_ok: bool = False, **kwargs: Any) -> ApiResponse:
        """Perform a DELETE and return an ApiResponse."""
        return self._request("DELETE", path, retry_until_ok=retry_until_ok, **kwargs)


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


def _response_code(response: requests.Response) -> Any:
    """The API's real status (responseCode) from the JSON body, or None."""
    try:
        body = response.json()
    except ValueError:
        return None
    return body.get("responseCode") if isinstance(body, dict) else None


def _response_message(response: requests.Response) -> Any:
    """The API's message from the JSON body, or None."""
    try:
        body = response.json()
    except ValueError:
        return None
    return body.get("message") if isinstance(body, dict) else None


def _should_retry(response: requests.Response, retry_until_ok: bool) -> bool:
    """Whether a (successfully received) response should be retried.

    - 5xx responseCodes are always retried
    - Any error responseCode is retried only when the caller sets retry_until_ok (left False
    for negative tests to get their 4xx returns immediately
    """
    code = _response_code(response)
    if code in _TRANSIENT_CODES:
        return True
    return retry_until_ok and isinstance(code, int) and code >= 400
