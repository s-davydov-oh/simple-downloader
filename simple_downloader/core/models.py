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
    name: str
    url: URL
    file_urls: Iterator[URL]


@dataclass(frozen=True, slots=True)
class MediaFile:
    name: str
    filename: Filename
    url: URL
    stream_url: URL
