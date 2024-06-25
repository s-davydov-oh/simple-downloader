from http import HTTPStatus
from logging import getLogger
from typing import Any, Literal

from fake_useragent import UserAgent
from requests import ConnectionError, HTTPError, Response, Session, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from yarl import URL

from simple_downloader.config import DELAY, MAX_REDIRECTS, RETRY_STRATEGY, TIMEOUT, TOTAL_RETRIES
from simple_downloader.core.exceptions import CustomHTTPError, EmptyContentType
from simple_downloader.core.logs import log_retry_request, log_request
from simple_downloader.core.utils import apply_delay


logger = getLogger(__name__)

SESSION = Session()
SESSION.max_redirects = MAX_REDIRECTS

SESSION.headers.update({"user-agent": UserAgent().random})
logger.debug("Session is open".upper())
logger.debug("Client parameters user %s", SESSION.headers)

RETRY_CODES = frozenset(
    {
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }
)


def requester(
    url: URL,
    method: Literal["get"] = "get",
    delay: float | tuple[float, float] | None = DELAY,
    timeout: tuple[float, float] = TIMEOUT,
    **kwargs: Any,
) -> Response:
    apply_delay(delay)

    @retry(
        reraise=True,
        stop=stop_after_attempt(TOTAL_RETRIES),
        wait=wait_exponential(**RETRY_STRATEGY),
        retry=retry_if_exception_type((ConnectionError, CustomHTTPError, Timeout)),
        before=log_request,
        before_sleep=log_retry_request,
    )
    def make_request(url: URL) -> Response:
        response = SESSION.request(method, str(url), timeout=timeout, **kwargs)
        _raise_http_exception(response)
        return response

    return make_request(url)


def _raise_http_exception(response: Response) -> None:
    try:
        response.raise_for_status()
    except HTTPError as e:
        if e.response.status_code in RETRY_CODES:
            if e.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                sleep_time_to_next = int(e.response.headers.get("retry-after", 0))
                apply_delay(sleep_time_to_next)

            error_message = str(e)
            raise CustomHTTPError(error_message, **e.__dict__)
        raise

    if not response.headers.get("content-type"):
        logger.debug("HTTP response headers %s", response.headers)
        raise EmptyContentType
