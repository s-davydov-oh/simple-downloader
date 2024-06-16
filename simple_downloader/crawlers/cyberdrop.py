from typing import Iterator

from bs4 import BeautifulSoup
from yarl import URL

from simple_downloader.core.exceptions import InvalidMediaType, ParsingError
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import parse_title
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
                    title=parse_title(soup),
                    url=url,
                    file_urls=self._parse_file_urls(soup),
                )
            case "f":
                api = self.BASE_API.joinpath(url.path[1:])
                json = requester(api).json()
                return MediaFile(
                    title=json["name"],
                    filename=parse_filename(json["name"]),
                    url=url,
                    stream_url=json["url"],
                )
            case _:
                raise InvalidMediaType(media_type, url)

    def _parse_file_urls(self, soup: BeautifulSoup) -> Iterator[URL]:
        a_tags = soup.select("#table .image")
        if not a_tags:
            raise ParsingError("File table not found")

        for a_tag in a_tags:
            yield URL(self.base_url.with_path(a_tag["href"]))  # type: ignore[reportArgumentType]
