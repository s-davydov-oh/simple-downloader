from yarl import URL

from simple_downloader.core.exceptions import UndefinedMediaTypeError
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import get_soup, parse_file_urls, parse_filename, parse_title


class Cyberdrop(Crawler):
    BASE_API = URL("https://cyberdrop.me/api")

    def get_media(self, url: URL) -> MediaAlbum | MediaFile:
        return self._parse_media(url)

    def _parse_media(self, url: URL) -> MediaAlbum | MediaFile:
        media_type = url.parts[1]
        match media_type:
            case "a":
                return self._parse_album(url)
            case "f":
                return self._parse_file(url)
            case _:
                raise UndefinedMediaTypeError(url, media_type)

    def _parse_album(self, url: URL) -> MediaAlbum:
        soup = get_soup(self.http_client.get_response(url).text)
        return MediaAlbum(
            title=parse_title(soup),
            url=url,
            file_urls=parse_file_urls(soup, "#table .image", url.origin()),
        )

    def _parse_file(self, url: URL) -> MediaFile:
        api = self.BASE_API.joinpath(url.path[1:])  # [1] is "/"
        json = self.http_client.get_response(api).json()
        return MediaFile(
            title=json["name"],
            filename=parse_filename(json["name"]),
            url=url,
            stream_url=json["url"],
        )
