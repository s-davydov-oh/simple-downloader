from dataclasses import dataclass, field
from functools import wraps
from http import HTTPStatus
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, ParamSpec, assert_never

from requests import ConnectionError, HTTPError, RequestException, TooManyRedirects, Timeout
from yarl import URL

from simple_downloader.config import MAX_REDIRECTS, TIMEOUT
from simple_downloader.core import exceptions as excs
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.utils import get_updated_parent_path, get_url_from_args
from simple_downloader.handlers import downloader, factory


P = ParamSpec("P")

logger = getLogger(__name__)


def error_handling_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        url = get_url_from_args(args)

        try:
            return func(*args, **kwargs)

        except HTTPError as e:
            logger.debug(e)
            code = e.response.status_code
            logger.info("[-] %s (%s): %s", HTTPStatus(code).phrase, code, url)
        except TooManyRedirects as e:
            logger.debug(e)
            logger.info("[-] Too Many Redirects (max %s): %s", MAX_REDIRECTS, url)
        except Timeout as e:
            logger.debug(e)
            logger.info("[-] Connect and read Timeout %s: %s", TIMEOUT, url)
        except (ConnectionError, excs.EmptyContentType) as e:
            logger.debug(e)
            logger.info("[-] Server Error: %s", url)
        except RequestException as e:
            logger.warning(e, exc_info=True)
            logger.info("[-] Download Error: %s", url)

        except excs.CrawlerNotFound as e:
            logger.debug(e)
            logger.info("[-] Hosting isn't supported: %s", url)
        except excs.ExtensionNotFound as e:
            logger.debug(e)
            logger.info("[-] File doesn't have an extension: %s", url)
        except excs.ExtensionNotSupported as e:
            logger.debug(e)
            logger.info("[-] File extension isn't supported: %s", url)
        except excs.FileOpenError as e:
            logger.debug(e)
            logger.info("[-] Save Error: %s", url)

    return wrapper


@dataclass
class Manager:
    save_path: Path
    crawler: Crawler = field(init=False)

    @error_handling_wrapper
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

    @error_handling_wrapper
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
