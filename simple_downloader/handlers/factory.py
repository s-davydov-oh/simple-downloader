from logging import getLogger
from re import search

from yarl import URL

from simple_downloader import crawlers
from simple_downloader.core.exceptions import CrawlerNotFoundError
from simple_downloader.core.models import Crawler

logger = getLogger(__name__)

HOST_MAPPING = {
    "cyberdrop": crawlers.Cyberdrop,
}


def get_crawler(url: URL) -> Crawler:
    def choice_crawler() -> type[Crawler]:
        if url.host is not None:
            for host_pattern, crawler in HOST_MAPPING.items():
                if search(host_pattern, url.host):
                    logger.debug("Received <%s> crawler for %s", crawler.__module__, url)
                    return crawler

        raise CrawlerNotFoundError(f"Crawler not found for {url}")

    return choice_crawler()(url.origin())
