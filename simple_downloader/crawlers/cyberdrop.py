from typing import Iterator

from bs4 import BeautifulSoup
from yarl import URL

from simple_downloader.core.exceptions import InvalidMediaType, ParsingError
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.utils import parse_filename
from simple_downloader.handlers.requester import requester


class Cyberdrop(Crawler):
    BASE_API = URL("https://cyberdrop.me/api")

    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile:
        media_type = url.parts[1]
        match media_type:
            case "a":
                soup = BeautifulSoup(requester(url).text, "lxml")
                return MediaAlbum(
                    title=self._parse_title(soup),
                    url=url,
                    file_urls=self._parse_file_urls(soup),
                )
            case "f":
                api = self.BASE_API.with_path(url.path[1:])
                json = requester(api).json()
                return MediaFile(
                    title=json["name"],
                    filename=parse_filename(json["name"]),
                    url=url,
                    stream_url=json["url"],
                )
            case _:
                raise InvalidMediaType

    @staticmethod
    def _parse_title(soup: BeautifulSoup) -> str:
        h1_tag = soup.select_one("h1")
        if h1_tag is None:
            raise ParsingError("<h1> tag not found")

        return h1_tag.getText(strip=True)

    def _parse_file_urls(self, soup: BeautifulSoup) -> Iterator[URL]:
        a_tags = soup.select("#table .image")
        if not a_tags:
            raise ParsingError("File table not found")

        for a_tag in a_tags:
            yield URL(self.base_url.with_path(a_tag["href"]))  # type: ignore[reportArgumentType]