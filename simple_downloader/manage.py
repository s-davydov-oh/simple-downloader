from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import ParamSpec, assert_never

from yarl import URL

from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.utils import get_updated_parent_path
from simple_downloader.handlers import downloader, factory


P = ParamSpec("P")

logger = getLogger(__name__)


@dataclass
class Manager:
    save_path: Path
    crawler: Crawler = field(init=False)

    def startup(self, task: URL) -> None:
        self.crawler = factory.get_crawler(task)

        media = self.crawler.scrape_media(task)
        match media:
            case MediaAlbum():
                self.save_path = get_updated_parent_path(self.save_path, media.title)
                [self._download(file_url) for file_url in media.file_urls]
            case MediaFile():
                self._download(media)
            case _ as unreachable:
                assert_never(unreachable)

    def _download(self, item: URL | MediaFile) -> None:
        file: MediaFile  # separate var because otherwise "pyright" says "reportRedeclaration".
        match item:
            case URL():
                file = self.crawler.scrape_media(item)  # type: ignore[reportAssignmentType]
            case MediaFile():
                file = item
            case _ as unreachable:
                assert_never(unreachable)

        downloader.download(file, self.save_path)
