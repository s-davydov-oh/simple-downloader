from typing import Iterator

from bs4 import BeautifulSoup
from yarl import URL

from simple_downloader.core.exceptions import FileTableNotFound, InvalidMediaType
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import parse_download_hyperlink, parse_title
from simple_downloader.core.utils import parse_filename
from simple_downloader.handlers.requester import requester


class Bunkr(Crawler):
    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile:
        soup = BeautifulSoup(requester(url).text, "lxml")
        title = parse_title(soup)
        media_type = url.parts[1]
        match media_type:
            case "a":
                return MediaAlbum(
                    title=title,
                    url=url,
                    file_urls=self._parse_file_urls(soup),
                )
            case "i" | "v" | "d":
                return MediaFile(
                    title=title,
                    filename=parse_filename(title),
                    url=url,
                    stream_url=self._parse_stream_url(soup),
                )
            case _:
                raise InvalidMediaType(media_type, url)

    @staticmethod
    def _parse_file_urls(soup: BeautifulSoup) -> Iterator[URL]:
        a_tags_with_file_urls = soup.select(".grid-images a")
        if not a_tags_with_file_urls:
            raise FileTableNotFound

        for a_tag in a_tags_with_file_urls:
            yield URL(a_tag["href"])  # type: ignore[reportArgumentType]

    @staticmethod
    def _parse_stream_url(soup: BeautifulSoup) -> URL:
        fileserver_url = parse_download_hyperlink(soup)
        soup = BeautifulSoup(requester(fileserver_url).text, "lxml")
        return parse_download_hyperlink(soup)
