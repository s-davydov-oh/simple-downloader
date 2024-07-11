from yarl import URL

from simple_downloader.core.exceptions import UndefinedMediaTypeError
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import get_soup, parse_file_urls, parse_filename, parse_title


BASE_API = URL("https://cyberdrop.me/api")


class Cyberdrop(Crawler):
    def get_media(self, url: URL) -> MediaAlbum | MediaFile:
        media_type = url.parts[1]
        match media_type:
            case "a":
                return self._parse_album(url)
            case "f":
                return self._parse_file(url)
            case _:
                raise UndefinedMediaTypeError(url, media_type)

    def _parse_album(self, album_url: URL) -> MediaAlbum:
        soup = get_soup(self.http_client.get_response(album_url).text)
        return MediaAlbum(
            title=parse_title(soup),
            url=album_url,
            file_urls=parse_file_urls(soup, "#table .image", album_url.origin()),
        )

    def _parse_file(self, file_url: URL) -> MediaFile:
        api = BASE_API.joinpath(file_url.path[1:])  # [1] is "/"
        file_info = self.http_client.get_response(api).json()
        return MediaFile(
            title=file_info["name"],
            filename=parse_filename(file_info["name"]),
            url=file_url,
            stream_url=file_info["url"],
        )
