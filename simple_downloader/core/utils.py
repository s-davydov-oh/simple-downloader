from re import compile
from yarl import URL

from simple_downloader.core.exceptions import ExtensionNotFound
from simple_downloader.core.models import Extension, Filename

FILENAME = compile(r"(.*)(\.\w+$)")


def get_url_from_args(arguments: tuple) -> URL | str:
    for arg in arguments:
        if isinstance(arg, URL):
            return arg

    return "<unknown URL>"


def parse_filename(name: str) -> Filename:
    match = FILENAME.search(name)
    if match is not None:
        stem, ext = match.groups()
        return Filename(stem, Extension(ext))

    raise ExtensionNotFound(f'File "{name}" doesn\'t have an extension')
