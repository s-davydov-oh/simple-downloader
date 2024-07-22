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
    TooManyRedirects,
)
from yarl import URL

from simple_downloader.config import (
    BASE_DIR,
    FAILURE,
    INFO,
    MAX_REDIRECTS,
    SAVE_FOLDER_NAME,
    UNKNOWN,
)
from simple_downloader.core.exceptions import (
    CrawlerNotFound,
    DeviceSpaceRunOutError,
    DownloadError,
    EmptyContentTypeError,
    ExtensionNotFoundError,
    ExtensionNotSupported,
    FileOpenError,
)
from simple_downloader.core.log_settings import LOGGING
from simple_downloader.core.models import Crawler, DownloadCounter, MediaAlbum, MediaFile
from simple_downloader.core.utils import (
    get_http_status_phrase,
    get_updated_parent_path,
    get_url_from_args,
)
from simple_downloader.handlers import downloader, factory, requester

P = ParamSpec("P")

config.dictConfig(LOGGING)
logger = getLogger("simple_downloader")


def error_handling_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Intercepts all major exceptions and logs them to a log file and the CLI.

    Allows you to continue running the program even if there is a failed request.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        url = get_url_from_args(args)

        try:
            return func(*args, **kwargs)

        except ExtensionNotFoundError as e:
            logger.info(e)
            click.echo(f'{FAILURE} File "{e.title}" has no extension: {url}')
        except ExtensionNotSupported as e:
            logger.info(e)
            click.echo(f'{FAILURE} File extension "{e.extension}" is not supported: {url}')
        except FileOpenError as e:
            logger.info(e)
            click.echo(f"{FAILURE} Filename has forbidden chars: {url}")

        except HTTPError as e:
            logger.info(e)
            code = e.response.status_code
            phrase = get_http_status_phrase(code)
            click.echo(f"{FAILURE} {phrase} ({code} code): {url}")
        except TooManyRedirects as e:
            logger.info(e)
            click.echo(f"{FAILURE} Too Many Redirects (max {MAX_REDIRECTS}): {url}")
        except ConnectTimeout as e:
            logger.info(e)
            click.echo(f"{FAILURE} Connect Timeout: {url}")
        except ReadTimeout as e:
            logger.info(e)
            click.echo(f"{FAILURE} Read Timeout: {url}")
        except (ConnectionError, EmptyContentTypeError) as e:
            logger.info(e)
            click.echo(f"{FAILURE} Unknown Server Error: {url}")
        except (RequestException, DownloadError) as e:
            logger.warning(e, exc_info=True)
            click.echo(f"{FAILURE} Download Error: {url}")

    return wrapper


@error_handling_wrapper
def download(
    url: URL,
    save_path: Path,
    crawler: Crawler,
    http_client: requester.Requester,
    counter: DownloadCounter,
) -> None:
    counter.add_attempt()

    media: MediaAlbum | MediaFile = crawler.get_media(url)
    match media:
        case MediaAlbum():
            save_path = get_updated_parent_path(save_path, media.title)
            for file_url in media.file_urls:
                download(file_url, save_path, crawler, http_client, counter)

        case MediaFile():
            downloader.download(media, save_path, http_client)
            if media.is_downloaded:
                counter.add_success()

        case _ as unreachable:
            assert_never(unreachable)


@click.command()
@click.argument("url", type=URL)
@click.option(
    "--save_path",  # if the "path" contains "\s", it must be framed with quotes
    "-p",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=get_updated_parent_path(BASE_DIR, SAVE_FOLDER_NAME),
)
def main(url: URL, save_path: Path) -> None:
    logger.info("Start task %s", url)
    click.echo(f"Task... {url}")
    click.echo(f'Path to the saved files is "{save_path}".\n')

    counter = DownloadCounter()

    with requester.Requester() as http_client:
        try:
            crawler = factory.get_crawler(url, http_client)
        except CrawlerNotFound as e:
            logger.info(e)
            click.echo(f"{FAILURE} Hosting is not supported: {e.url}", err=True)
        else:
            try:
                download(url, save_path, crawler, http_client, counter)
            except DeviceSpaceRunOutError as e:
                logger.warning(e)
                click.echo(f"{FAILURE} Save Error: Probably not enough free space", err=True)
                sys.exit(1)
            finally:
                click.echo(
                    f"\n{INFO} Completed: "
                    f"{counter.successes} successfully downloaded, "
                    f"{counter.failures} failed attempts.",
                )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("There was an unexpected error")
        click.echo(f"{UNKNOWN} Unknown Error: Please report it to the developer", err=True)
        sys.exit(1)
