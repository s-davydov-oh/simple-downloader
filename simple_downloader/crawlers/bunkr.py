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
        response = self.http_client.get_response(url)
        url_after_redirects = URL(response.url)  # a lot of old urls whose media type is not parsed
        soup = get_soup(response.text)
        return self._parse_media(url_after_redirects, soup)

    def _parse_media(self, url: URL, soup: BeautifulSoup) -> MediaAlbum | MediaFile:
        media_type = url.parts[1]
        match media_type:
            case "a":
                return self._parse_album(url, soup)
            case "i" | "v" | "d":
                return self._parse_file(url, soup)
            case _:
                raise UndefinedMediaTypeError(url, media_type)

    @staticmethod
    def _parse_album(url: URL, soup: BeautifulSoup) -> MediaAlbum:
        return MediaAlbum(
            title=parse_title(soup),
            url=url,
            file_urls=parse_file_urls(soup, ".grid-images a"),
        )

    def _parse_file(self, url: URL, soup: BeautifulSoup) -> MediaFile:
        title = parse_title(soup)
        return MediaFile(
            title=title,
            filename=parse_filename(title),
            url=url,
            stream_url=self._parse_stream_url(soup),
        )

    def _parse_stream_url(self, soup: BeautifulSoup) -> URL:
        url_with_hyperlink = parse_download_hyperlink(soup)
        soup = get_soup(self.http_client.get_response(url_with_hyperlink).text)
        return parse_download_hyperlink(soup)
