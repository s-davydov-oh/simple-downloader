from re import compile
from yarl import URL

from simple_downloader.core.exceptions import ExtensionNotFound
from simple_downloader.core.models import Extension, Filename


FILENAME = compile(r"(.*)(\.\w+$)")
FORBIDDEN = '/<>:"\\|?*'  # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words


def get_url_from_args(arguments: tuple) -> URL | str:
    for arg in arguments:
        if isinstance(arg, URL):
            return arg

    return "<unknown URL>"


def parse_filename(name: str) -> Filename:
    match = FILENAME.search(name)
    if match is not None:
        stem, ext = match.groups()
        return Filename(sanitize(stem), Extension(ext))

    raise ExtensionNotFound(f'File "{name}" doesn\'t have an extension')


def sanitize(name: str, separator: str = "_") -> str:
    """Removes all forbidden chars for the dir name and filename."""

    name = "".join(separator if char in FORBIDDEN else char for char in name)
    return name.rstrip(".").strip()
