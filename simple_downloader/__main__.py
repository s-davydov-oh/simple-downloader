import sys

from simple_downloader.core.logging_settings import logging


logger = logging.getLogger("simple_downloader")


def main() -> None: ...


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("There was an unexpected error")
        logger.info("[?] Unknown Error: Please report it to the developer")
        sys.exit(1)
