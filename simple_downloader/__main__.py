from functools import wraps
from logging import config, getLogger
from pathlib import Path
import sys
from typing import Any, Callable, ParamSpec, assert_never

import click
from requests import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
    RequestException,
    Timeout,
    TooManyRedirects,
)
from yarl import URL

from simple_downloader.config import (
    BASE_DIR,
    FAILED,
    MAX_REDIRECTS,
    SAVE_FOLDER_NAME,
    TIMEOUT,
    UNKNOWN,
)
from simple_downloader.core.exceptions import (
    CrawlerNotFound,
    DeviceSpaceRunOutError,
    EmptyContentTypeError,
    ExtensionNotFoundError,
    ExtensionNotSupported,
    FileOpenError,
)
from simple_downloader.core.logging_settings import LOGGING
from simple_downloader.core.models import Crawler, MediaAlbum, MediaFile
from simple_downloader.core.utils import (
    print_to_cli,
    get_http_status_phrase,
    get_updated_parent_path,
    get_url_from_args,
)
from simple_downloader.handlers import downloader, factory, requester


P = ParamSpec("P")

config.dictConfig(LOGGING)
logger = getLogger("simple_downloader")


def error_handling_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        url = get_url_from_args(args)

        try:
            return func(*args, **kwargs)

        except HTTPError as e:
            logger.debug(e)
            code = e.response.status_code
            phrase = get_http_status_phrase(code)
            print_to_cli(f"{FAILED} {phrase} ({code} code): {url}")
        except TooManyRedirects as e:
            logger.debug(e)
            print_to_cli(f"{FAILED} Too Many Redirects (max {MAX_REDIRECTS}): {url}")
        except Timeout as e:
            logger.debug(e)
            connect, read = TIMEOUT
            match e:
                case ConnectTimeout():
                    print_to_cli(f"{FAILED} Connect Timeout ({connect} seconds): {url}")
                case ReadTimeout():
                    print_to_cli(f"{FAILED} Read Timeout ({read} seconds): {url}")
        except (ConnectionError, EmptyContentTypeError) as e:
            logger.debug(e)
            print_to_cli(f"{FAILED} Unknown Server Error: {url}")
        except RequestException as e:
            logger.warning(e, exc_info=True)
            print_to_cli(f"{FAILED} Download Error: {url}")

        except ExtensionNotFoundError as e:
            logger.debug(e)
            print_to_cli(f'{FAILED} File "{e.title}" has no extension: {url}')
        except ExtensionNotSupported as e:
            logger.debug(e)
            print_to_cli(f'{FAILED} File extension "{e.extension}" is not supported: {url}')
        except FileOpenError as e:
            logger.debug(e)
            print_to_cli(f"{FAILED} Filename has forbidden chars: {url}")

    return wrapper


@error_handling_wrapper
def download(url: URL, save_path: Path, crawler: Crawler, http_client: requester.Requester) -> None:
    media = crawler.scrape_media(url)
    match media:
        case MediaAlbum():
            save_path = get_updated_parent_path(save_path, media.title)
            [download(file_url, save_path, crawler, http_client) for file_url in media.file_urls]
        case MediaFile():
            downloader.download(media, save_path, http_client)
        case _ as unreachable:
            assert_never(unreachable)


@click.command()
@click.argument("url", type=URL)
@click.option(
    "--path",  # if the "path" contains "\s", it must be framed with quotes
    "-p",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=get_updated_parent_path(BASE_DIR, SAVE_FOLDER_NAME),
)
def main(url: URL, path: Path) -> None:
    logger.info("Start downloading %s", url)
    print_to_cli(f'Downloading {url}\nSave path "{path}"')
    print_to_cli("-" * 20)

    with requester.Requester() as http_client:
        try:
            crawler: Crawler = factory.get_crawler(url, http_client)
        except CrawlerNotFound as e:
            logger.debug(e)
            print_to_cli(f"{FAILED} Hosting is not supported: {e.url}")
        else:
            try:
                download(url, path, crawler, http_client)
            except DeviceSpaceRunOutError as e:
                logger.warning(e, exc_info=True)
                print_to_cli(f"{FAILED} Save Error: Probably not enough free space")
                sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("There was an unexpected error")
        print_to_cli(f"{UNKNOWN} Unknown Error: Please report it to the developer")
        sys.exit(1)
