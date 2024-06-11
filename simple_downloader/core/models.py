from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

from yarl import URL


@dataclass(frozen=True, slots=True)
class Filename:
    stem: str
    extension: str

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


class Crawler(ABC):  # if you use @dataclass, an "unexpected argument" for an obj attribute.
    def __init__(self, base_url: URL) -> None:
        self.base_url = base_url

    @abstractmethod
    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile: ...
