from dataclasses import dataclass

from yarl import URL

from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile


@dataclass
class Cyberdrop(Crawler):
    def scrape_media(self, url: URL) -> MediaAlbum | MediaFile: ...
