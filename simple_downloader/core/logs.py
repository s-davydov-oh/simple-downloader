from logging import getLogger

from tenacity import RetryCallState

from simple_downloader.core.utils import get_url_from_args


logger = getLogger(__name__)


def log_request(retry_state: RetryCallState) -> None:
    """
    Logging the request using tenacity.retry(before=).

    It is expected that the function which uses logging has a URL as one of its parameters,
    either in media format or as a yarl.URL() object.
    """

    url = get_url_from_args(retry_state.args)
    attempt = retry_state.attempt_number

    logger.info("Request has been sent to %s, this is the %s attempt", url, attempt)


def log_download(retry_state: RetryCallState) -> None:
    """
    Logging the start of a file download using tenacity.retry(before=).

    It is expected that the function which uses logging has a URL as one of its parameters,
    either in media format or as a yarl.URL() object.
    """

    url = get_url_from_args(retry_state.args)
    attempt = retry_state.attempt_number

    logger.info("Downloading %s, this is the %s attempt", url, attempt)


def log_retry(retry_state: RetryCallState) -> None:
    """
    Logging the retry using tenacity.retry(before_sleep=).

    Source tenacity.before_sleep_log.
    """

    if retry_state.outcome is None:
        raise RuntimeError(f"<{__name__}> called before outcome was set")

    if retry_state.next_action is None:
        raise RuntimeError(f"<{__name__}> called before next_action was set")

    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        verb, value = "raised", f"{exception.__class__.__name__}: {exception}"
    else:
        verb, value = "returned", retry_state.outcome.result()

    logger.info("Retry in %s seconds as it %s %s", retry_state.next_action.sleep, verb, value)
