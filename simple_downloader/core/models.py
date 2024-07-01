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


@dataclass(frozen=True, slots=True)
class MediaFile:
    title: str
    filename: Filename
    url: URL
    stream_url: URL


# if u use @dataclass, there will be an "unexpected argument" when init the object
class Crawler(ABC):
    def __init__(self, base_url: URL, http_client: "Requester") -> None:
        self.base_url = base_url
        self.http_client = http_client

    @abstractmethod
    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile: ...
