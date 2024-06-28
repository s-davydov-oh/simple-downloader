from bs4 import BeautifulSoup
from yarl import URL

from simple_downloader.core.exceptions import UndefinedMediaTypeError
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import (
    get_soup,
    parse_download_hyperlink,
    parse_file_urls,
    parse_filename,
    parse_title,
)


class Bunkr(Crawler):
    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile:
        soup = get_soup(self.http_client.get_response(url).text)
        title = parse_title(soup)
        media_type = url.parts[1]
        match media_type:
            case "a":
                return MediaAlbum(
                    title=title,
                    url=url,
                    file_urls=parse_file_urls(soup, ".grid-images a"),
                )
            case "i" | "v" | "d":
                return MediaFile(
                    title=title,
                    filename=parse_filename(title),
                    url=url,
                    stream_url=self._parse_stream_url(soup),
                )
            case _:
                raise UndefinedMediaTypeError(url, media_type)

    def _parse_stream_url(self, soup: BeautifulSoup) -> URL:
        fileserver_url = parse_download_hyperlink(soup)
        soup = get_soup(self.http_client.get_response(fileserver_url).text)
        return parse_download_hyperlink(soup)
