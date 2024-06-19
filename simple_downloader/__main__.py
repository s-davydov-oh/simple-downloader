from pathlib import Path
import sys

import click
from yarl import URL

from simple_downloader.config import BASE_DIR, SAVE_FOLDER_NAME
from simple_downloader.core.exceptions import DeviceSpaceRunOutError
from simple_downloader.core.logging_settings import logging
from simple_downloader.core.utils import get_updated_parent_path
from simple_downloader.handlers.requester import SESSION
from simple_downloader.manage import Manager


# otherwise logging code in "requester" is executed before the logger creation in "__main__.py".
logger = logging.getLogger("simple_downloader")


@click.command()
@click.argument("url", type=URL)
@click.option(
    "--path",  # if the "path" contains "\s", it must be framed with quotes.
    "-p",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=get_updated_parent_path(BASE_DIR, SAVE_FOLDER_NAME),
)
def main(url: URL, path: Path) -> None:
    manager = Manager(path)
    manager.startup(url)


if __name__ == "__main__":
    try:
        main()
    except DeviceSpaceRunOutError as e:
        logger.exception(e)
        logger.info("[-] Save Error: Probable no space left on device")
        sys.exit(1)
    except Exception:
        logger.exception("There was an unexpected error")
        logger.info("[?] Unknown Error: Please report it to the developer")
        sys.exit(1)
    finally:
        SESSION.close()
        logger.debug("Session is closed".upper())
