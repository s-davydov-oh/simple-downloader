from bs4 import BeautifulSoup
from yarl import URL

from simple_downloader.core.exceptions import InvalidMediaType
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import parse_file_urls, parse_filename, parse_title
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
                    file_urls=parse_file_urls(soup, "#table .image", self.base_url),
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
