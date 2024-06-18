from logging import getLogger
from pathlib import Path

from yarl import URL

from simple_downloader.config import DEFAULT_ALBUM_NAME
from simple_downloader.core.models import MediaAlbum, MediaFile


logger = getLogger(__name__)

FORBIDDEN = '/<>:"\\|?*'  # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words


def get_updated_parent_path(parent_path: Path, parent_name: str = DEFAULT_ALBUM_NAME) -> Path:
    correct_parent_name = sanitize(parent_name)
    updated_parent_path = parent_path.joinpath(correct_parent_name)

    try:
        updated_parent_path.mkdir(exist_ok=True, parents=True)
    except IOError as e:
        logger.debug(e)
        updated_parent_path = get_updated_parent_path(parent_path)

    logger.debug('Updated save path "%s"', updated_parent_path)
    return updated_parent_path


def get_url_from_args(arguments: tuple) -> URL | str:
    for arg in arguments:
        if isinstance(arg, URL):
            return arg
        if isinstance(arg, MediaAlbum | MediaFile):
            return arg.url

    return "<unknown URL>"


def sanitize(name: str, separator: str = "_") -> str:
    """Removes all forbidden chars for the dir name and filename."""

    name = "".join(separator if char in FORBIDDEN else char for char in name)
    return name.rstrip(".").strip()


def decode_cloudflare_email_protection(encoded_data: str) -> str:
    """
    Cloudflare email protection decoding algorithm.
    Source https://usamaejaz.com/cloudflare-email-decoding.
    """

    r = int(encoded_data[:2], 16)
    chars = [chr(int(encoded_data[i : i + 2], 16) ^ r) for i in range(2, len(encoded_data), 2)]
    return "".join(chars)
