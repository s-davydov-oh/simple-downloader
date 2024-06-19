from pathlib import Path

from yarl import URL


class CrawlerNotFound(Exception):
    """No crawler was found for the hosting."""

    def __init__(self, url: URL) -> None:
        self.url = url
        super().__init__(f"Crawler not found for {self.url}")


class ExtensionNotFound(Exception):
    """The file doesn't have an extension."""

    def __init__(self, title: str) -> None:
        self.title = title
        super().__init__(f'"File "{self.title}" doesn\'t have an extension"')


class ExtensionNotSupported(Exception):
    """The extension is not in the list of "supported extensions"."""

    def __init__(self, extension: str) -> None:
        self.extension = extension
        super().__init__(f'File extension "{self.extension}" isn\'t supported')


class EmptyContentType(Exception):
    """The server returned an empty "content-type"."""

    def __init__(self) -> None:
        super().__init__("Server returned an unexpected content-type")


class InvalidMediaType(Exception):
    """Crawler can't identify the media type."""

    def __init__(self, media_type: str, url: URL) -> None:
        self.media_type = media_type
        self.url = url
        super().__init__(f'Cannot identify media type for "{self.media_type}": {self.url}')


class ParsingError(Exception):
    """Probably a parsing problem with the Crawler."""

    def __init__(self, message: str = "Unknown parsing error") -> None:
        super().__init__(message)


class FileTableNotFound(ParsingError):
    """The file table in an album was not found."""

    def __init__(self) -> None:
        super().__init__("File table not found")


class TitleNotFound(ParsingError):
    """Probably no <h1> tag found."""

    def __init__(self) -> None:
        super().__init__("<h1> tag not found")


class DownloadHyperlinkNotFound(ParsingError):
    """The hyperlink named "Download" wasn't found."""

    def __init__(self) -> None:
        super().__init__('The hyperlink named "Download" wasn\'t found')


class FileOpenError(Exception):
    """The error occurs when the file cannot be opened."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f'Unable to open a file: "{path}"')


class DeviceSpaceRunOutError(Exception):
    """The error occurs when the device runs out of space."""

    def __init__(self) -> None:
        super().__init__("No space left on device")
