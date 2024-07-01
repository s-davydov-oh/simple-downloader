from http import HTTPStatus
from logging import getLogger
from pathlib import Path
from random import uniform
from time import sleep

from yarl import URL

from simple_downloader.config import DEFAULT_ALBUM_NAME, DISABLE_CLI_MESSAGES
from simple_downloader.core.models import MediaAlbum, MediaFile


logger = getLogger(__name__)

ILLEGAL_CHARS = '/<>:"\\|?*'  # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words


def print_to_cli(message: str, disable: bool = DISABLE_CLI_MESSAGES) -> None:
    if disable is False:
        print(message)


def get_updated_parent_path(parent_path: Path, parent_name: str = DEFAULT_ALBUM_NAME) -> Path:
    """Updates the parent path and removes any invalid characters from the name."""

    correct_parent_name = sanitize(parent_name)
    updated_parent_path = parent_path.joinpath(correct_parent_name)

    try:
        updated_parent_path.mkdir(exist_ok=True, parents=True)
    except IOError as e:
        logger.debug(e)
        updated_parent_path = get_updated_parent_path(parent_path)

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

    name = "".join(separator if char in ILLEGAL_CHARS else char for char in name)
    return name.rstrip(".").strip()


def decode_cloudflare_email_protection(encoded_data: str) -> str:
    """
    The algorithm for decoding email protection provided by CloudFlare.

    Source https://usamaejaz.com/cloudflare-email-decoding.
    """

    mask = int(encoded_data[:2], 16)
    chars = [chr(int(encoded_data[i : i + 2], 16) ^ mask) for i in range(2, len(encoded_data), 2)]
    return "".join(chars)


def get_http_status_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "HTTP Error"
