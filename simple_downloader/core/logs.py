from logging import getLogger

from tenacity import RetryCallState

from simple_downloader.core.utils import get_url_from_args

logger = getLogger(__name__)


def log_request(retry_state: RetryCallState) -> None:
    """
    Logging sending a request via "tenacity.retry(before=)".
    It is expected that one of the arguments to the function to which the logging is applied is a URL.
    """

    url = get_url_from_args(retry_state.args)
    attempt = retry_state.attempt_number

    logger.debug("Request has been sent to %s, this is the %s attempt", url, attempt)


def log_retry_request(retry_state: RetryCallState) -> None:
    """
    Logging retry via “tenacity.retry(before_sleep=)”.
    Source "tenacity.before_sleep_log".
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

    logger.debug("Retry in %s second as it %s %s", retry_state.next_action.sleep, verb, value)
