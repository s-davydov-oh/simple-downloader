from http import HTTPStatus
from logging import getLogger
from types import TracebackType
from typing import Any, Literal, Self

from fake_useragent import UserAgent
from requests import ConnectionError, HTTPError, Response, Session, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from yarl import URL

from simple_downloader.config import DELAY, MAX_REDIRECTS, RETRY_STRATEGY, TIMEOUT, TOTAL_RETRIES
from simple_downloader.core.exceptions import CustomHTTPError, EmptyContentType
from simple_downloader.core.logs import log_retry_request, log_request
from simple_downloader.core.utils import apply_delay


logger = getLogger(__name__)

RETRY_CODES = frozenset(
    {
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }
)


class Requester:
    def __init__(
        self,
        headers: dict | None = None,
        delay: float | tuple[float, float] | None = DELAY,
        timeout: tuple[float, float] = TIMEOUT,
        max_redirects: int = MAX_REDIRECTS,
    ) -> None:
        self._session: Session = Session()
        logger.debug("Session is open".upper())

        self.client_headers = {"user-agent": UserAgent().random} if headers is None else headers
        self.delay = delay
        self.timeout = timeout
        self.max_redirects = max_redirects

        self._session.max_redirects = self.max_redirects
        self._session.headers.update(self.client_headers)
        logger.debug("Session parameters %s", self._session.headers)

    def close(self) -> None:
        self._session.close()
        logger.debug("Session is closed".upper())

    def get_response(self, url: URL, **kwargs: Any) -> Response:
        apply_delay(self.delay)
        return self._make_request("get", url, **kwargs)

    @retry(
        reraise=True,
        stop=stop_after_attempt(TOTAL_RETRIES),
        wait=wait_exponential(**RETRY_STRATEGY),
        retry=retry_if_exception_type((ConnectionError, CustomHTTPError, Timeout)),
        before=log_request,
        before_sleep=log_retry_request,
    )
    def _make_request(self, method: Literal["get"], url: URL, **kwargs: Any) -> Response:
        response = self._session.request(method, str(url), timeout=self.timeout, **kwargs)
        self._raise_http_exception(response)
        return response

    @staticmethod
    def _raise_http_exception(response: Response) -> None:
        try:
            response.raise_for_status()
        except HTTPError as e:
            if e.response.status_code in RETRY_CODES:
                if e.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    sleep_to_next = int(e.response.headers.get("retry-after", 0))
                    apply_delay(sleep_to_next)

                error_message = str(e)
                raise CustomHTTPError(error_message, **e.__dict__)
            raise

        if not response.headers.get("content-type"):
            logger.debug("HTTP response headers %s", response.headers)
            raise EmptyContentType

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            self.close()
