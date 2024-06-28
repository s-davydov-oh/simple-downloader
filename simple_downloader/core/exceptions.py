from pathlib import Path
from typing import Any

from requests import HTTPError
from yarl import URL


class DownloadError(Exception):
    """The error occurs if an ambiguous exception occurred during the file download process."""

    def __init__(self, message: str = "Something went wrong") -> None:
        super().__init__(message)


class CustomHTTPError(HTTPError):
    """
    Exception wrapper for HTTPError.

    The error occurs if the request fails and the response status code
    is included in the list of codes for which retry applies.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CrawlerNotFound(DownloadError):
    """The error occurs if the crawler was not found for the host."""

    def __init__(self, url: URL) -> None:
        self.url = url
        super().__init__(f"Crawler not found for {self.url}")


class EmptyContentTypeError(DownloadError):
    """The error occurs if the server returned an empty "content-type"."""

    def __init__(self) -> None:
        super().__init__('Server returned an empty "content-type"')


class UndefinedMediaTypeError(DownloadError):
    """The error occurs if the crawler is unable to determine the media type."""

    def __init__(self, url: URL, media_type: str) -> None:
        self.url = url
        self.media_type = media_type
        super().__init__(f'Undefined media type "{self.media_type}": {self.url}')


class ExtensionNotFoundError(DownloadError):
    """The error occurs if the received filename does not have an extension."""

    def __init__(self, title: str) -> None:
        self.title = title
        super().__init__(f'File "{self.title}" has not extension')


class ExtensionNotSupported(DownloadError):
    """The error occurs if the file extension is not in the supported list."""

    def __init__(self, extension: str) -> None:
        self.extension = extension
        super().__init__(f'File extension "{self.extension}" is not supported')


class FileOpenError(DownloadError):
    """The error occurs when a file cannot be opened."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f'Unable to open the file: "{path}"')


class DeviceSpaceRunOutError(DownloadError):
    """The error occurs when the device runs out of space."""

    def __init__(self) -> None:
        super().__init__("No space left on device")


# ------------------------------


class ParsingError(DownloadError):
    """The error occurs if an ambiguous error occurred during parsing."""

    def __init__(self, message: str = "Unknown parsing error") -> None:
        super().__init__(message)


class FileTableNotFoundError(ParsingError):
    """The error occurs if the file table is not found."""

    def __init__(self) -> None:
        super().__init__("File table not found")


class TitleNotFoundError(ParsingError):
    """The error occurs if the <h1> tag is not found."""

    def __init__(self) -> None:
        super().__init__("<h1> tag not found")


class HyperlinkNotFoundError(ParsingError):
    """The error occurs if a hyperlink  is not found."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f'Hyperlink named "{self.name}" was not found')
