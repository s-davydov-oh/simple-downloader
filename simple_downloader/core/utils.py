from http import HTTPStatus
from logging import getLogger
from pathlib import Path
from random import uniform
from time import sleep

from yarl import URL

from simple_downloader.config import DEFAULT_ALBUM_NAME
from simple_downloader.core.models import MediaAlbum, MediaFile


logger = getLogger(__name__)

ILLEGAL_CHARS = '/<>:"\\|?*'  # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words


def get_updated_parent_path(parent_path: Path, parent_name: str = DEFAULT_ALBUM_NAME) -> Path:
    """Updates the parent path and removes any invalid characters from the name."""

    valid_parent_path = sanitize(parent_name)
    updated_parent_path = parent_path.joinpath(valid_parent_path)

    try:
        updated_parent_path.mkdir(exist_ok=True, parents=True)
    except IOError as e:
        logger.debug(e)
        return get_updated_parent_path(parent_path)

    logger.debug('Updated path to the saved files will be "%s"', updated_parent_path)
    return updated_parent_path


def apply_delay(delay: float | tuple[float, float] | None) -> None:
    match delay:
        case float():
            sleep_time = delay
        case tuple():
            sleep_time = uniform(*delay)
        case _:
            sleep_time = 0

    logger.debug("Delay %s seconds", f"{sleep_time:.2f}")
    sleep(sleep_time)


def get_url_from_args(arguments: tuple) -> URL | str:
    for arg in arguments:
        if isinstance(arg, URL):
            return arg
        if isinstance(arg, MediaAlbum | MediaFile):
            return arg.url

    return "<unknown URL>"


def sanitize(name: str, separator: str = "_") -> str:
    """Removes illegal characters from the directory and filenames."""

    valid_name = "".join(separator if char in ILLEGAL_CHARS else char for char in name)
    return valid_name.rstrip(".").strip()


def decode_cloudflare_email_protection(encode_str: str) -> str:
    """
    The algorithm for decoding email protection provided by CloudFlare.

    Source https://usamaejaz.com/cloudflare-email-decoding.
    """

    mask = int(encode_str[:2], 16)
    return "".join(chr(int(encode_str[i : i + 2], 16) ^ mask) for i in range(2, len(encode_str), 2))


def get_http_status_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "HTTP Error"
