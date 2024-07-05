from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterator

from yarl import URL

from simple_downloader.config import SUPPORTED_EXTENSIONS
from simple_downloader.core.exceptions import ExtensionNotSupported

if TYPE_CHECKING:
    from simple_downloader.handlers.requester import Requester


@dataclass(frozen=True, slots=True)
class Extension:
    name_with_dot: str

    def __post_init__(self) -> None:
        if self.name_with_dot.lower() not in SUPPORTED_EXTENSIONS:
            raise ExtensionNotSupported(self.name_with_dot)

    def __str__(self) -> str:
        return self.name_with_dot


@dataclass(frozen=True, slots=True)
class Filename:
    stem: str
    extension: Extension

    def __str__(self) -> str:
        return f"{self.stem}{self.extension}"


@dataclass(frozen=True, slots=True)
class MediaAlbum:
    title: str
    url: URL
    file_urls: Iterator[URL]


@dataclass(slots=True)
class MediaFile:
    title: str
    filename: Filename
    url: URL
    stream_url: URL
    is_downloaded: bool = False

    def mark_downloaded(self) -> None:
        self.is_downloaded = True


@dataclass(slots=True)
class DownloadCounter:
    _attempts: int = 0
    successes: int = 0

    @property
    def attempts(self):
        # -1 in case an album is parsed (album is counted as a file)
        return self._attempts - 1 if self._attempts > 1 else self._attempts

    @property
    def failures(self) -> int:
        return self.attempts - self.successes

    def add_attempt(self) -> None:
        self._attempts += 1

    def add_success(self) -> None:
        self.successes += 1


@dataclass(frozen=True, slots=True)
class Crawler(ABC):
    http_client: "Requester"

    @abstractmethod
    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile: ...
