from typing import TypeAlias

from yarl import URL

from simple_downloader.core.exceptions import UndefinedMediaTypeError
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.parsing import parse_filename


Json: TypeAlias = dict

BASE_API = URL("https://pixeldrain.com/api")


class Pixeldrain(Crawler):
    def get_media(self, url: URL) -> MediaAlbum | MediaFile:
        if url.fragment:  # is this a part of the album?
            return self._parse_album_item(url)

        media_type = url.parts[1]
        match media_type:
            case "l":
                return self._parse_album(url)
            case "u":
                return self._parse_file(url)
            case _:
                raise UndefinedMediaTypeError(url, media_type)

    def _parse_album_item(self, item_url: URL) -> MediaFile:
        """
        The unique case of a URL is when it is not a separate file, but a file included in an album.
        This means that it must be handled differently, as it is not possible to easily obtain the file ID.
        """

        item_number = int(item_url.fragment.rsplit("=", 1)[1])  # fragment scheme "item={number}"
        album_info = self._get_album_info(item_url)
        file_id = album_info["files"][item_number]["id"]
        file_url = item_url.with_path(f"u/{file_id}")
        return self._parse_file(file_url)

    def _parse_album(self, album_url: URL) -> MediaAlbum:
        album_info = self._get_album_info(album_url)
        return MediaAlbum(
            title=album_info["title"],
            url=album_url,
            file_urls=(album_url.with_path(f'u/{f_info["id"]}') for f_info in album_info["files"]),
        )

    def _parse_file(self, file_url: URL) -> MediaFile:
        api = BASE_API.joinpath(f"file/{file_url.name}/info")
        file_info = self.http_client.get_response(api).json()
        return MediaFile(
            title=file_info["name"],
            filename=parse_filename(file_info["name"]),
            url=file_url,
            stream_url=BASE_API.joinpath(f"file/{file_url.name}"),
        )

    def _get_album_info(self, album_url: URL) -> Json:
        api = BASE_API.joinpath(f"list/{album_url.name}")
        return self.http_client.get_response(api).json()
