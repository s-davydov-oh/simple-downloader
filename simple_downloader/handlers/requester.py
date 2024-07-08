from http import HTTPStatus
from logging import getLogger
from types import TracebackType
from typing import Any, Literal, Self

from fake_useragent import UserAgent
from requests import ConnectionError, HTTPError, Response, Session, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from yarl import URL

from simple_downloader.config import (
    DEFAULT_DELAY,
    DEFAULT_TIMEOUT,
    MAX_REDIRECTS,
    RETRY_STRATEGY,
    TOTAL_RETRIES,
)
from simple_downloader.core.exceptions import CustomHTTPError, EmptyContentTypeError
from simple_downloader.core.logs import log_request, log_retry
from simple_downloader.core.utils import apply_delay


logger = getLogger(__name__)

RETRY_CODES = frozenset(
    {
        HTTPStatus.REQUEST_TIMEOUT,
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }
)


class Requester:
    def __init__(self, delay: float | tuple[float, float] | None = DEFAULT_DELAY) -> None:
        self._session: Session = Session()
        logger.debug("Session is open".upper())

        self.delay = delay

        self._session.max_redirects = MAX_REDIRECTS
        self._session.headers.update({"user-agent": UserAgent().random})
        logger.debug("Session parameters %s", self._session.headers)

    def close_session(self) -> None:
        self._session.close()
        logger.debug("Session is closed".upper())

    def get_response(self, url: URL, stream: bool = False) -> Response:
        apply_delay(self.delay)
        return self._make_request("get", url, stream=stream)

    @retry(
        reraise=True,
        stop=stop_after_attempt(TOTAL_RETRIES),
        wait=wait_exponential(**RETRY_STRATEGY),
        retry=retry_if_exception_type((ConnectionError, CustomHTTPError, Timeout)),
        before=log_request,
        before_sleep=log_retry,
    )
    def _make_request(self, method: Literal["get"], url: URL, **kwargs: Any) -> Response:
        response = self._session.request(method, str(url), timeout=DEFAULT_TIMEOUT, **kwargs)
        self._raise_http_exception(response)
        return response

    @staticmethod
    def _raise_http_exception(response: Response) -> None:
        try:
            response.raise_for_status()
        except HTTPError as e:
            if e.response.status_code in RETRY_CODES:
                if e.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    sleep_time_until_retry = int(e.response.headers.get("retry-after", 0))
                    apply_delay(sleep_time_until_retry)

                error_message = str(e)
                raise CustomHTTPError(error_message, **e.__dict__)  # unpacking for the parent class
            raise

        if not response.headers.get("content-type"):
            logger.debug("HTTP response headers %s", response.headers)
            raise EmptyContentTypeError

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            self.close_session()
