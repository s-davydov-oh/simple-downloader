from logging import getLogger
from random import uniform
from time import sleep
from typing import Any, Literal

from fake_useragent import UserAgent
from requests import Response, Session
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from yarl import URL

from simple_downloader.config import DELAY, MAX_REDIRECTS, RETRY_STRATEGY, TIMEOUT, TOTAL_RETRIES
from simple_downloader.core.exceptions import InvalidContentType
from simple_downloader.core.logs import log_retry_request, log_request


logger = getLogger(__name__)

SESSION = Session()
SESSION.max_redirects = MAX_REDIRECTS
SESSION.headers.update({"user-agent": UserAgent().random})
logger.debug("Session is open".upper())
logger.debug("Client parameters user %s", SESSION.headers)


def requester(
    url: URL,
    method: Literal["get"] = "get",
    delay: float | tuple[float, float] | None = DELAY,
    timeout: tuple[float, float] = TIMEOUT,
    **kwargs: Any,
) -> Response:
    match delay:
        case float():
            sleep_time = delay
        case tuple():
            sleep_time = uniform(*delay)
        case _:
            sleep_time = 0

    logger.debug("Delay before request %f second", sleep_time)
    sleep(sleep_time)

    @retry(
        reraise=True,
        stop=stop_after_attempt(TOTAL_RETRIES),
        wait=wait_exponential(**RETRY_STRATEGY),
        retry=retry_if_exception_type((ConnectionError, HTTPError, Timeout)),
        before=log_request,
        before_sleep=log_retry_request,
    )
    def make_request(url: URL) -> Response:
        response = SESSION.request(method, str(url), timeout=timeout, **kwargs)
        response.raise_for_status()

        if not response.headers.get("content-type"):
            logger.debug("HTTP response headers %s", response.headers)
            raise InvalidContentType("Server returned an unexpected content-type")

        return response

    return make_request(url)
