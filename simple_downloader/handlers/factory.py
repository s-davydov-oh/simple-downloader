from logging import getLogger

from yarl import URL

from simple_downloader import crawlers
from simple_downloader.core.exceptions import CrawlerNotFound
from simple_downloader.core.models import Crawler
from simple_downloader.handlers.requester import Requester


logger = getLogger(__name__)

MAPPING = {
    "cyberdrop": crawlers.Cyberdrop,
    "bunkr": crawlers.Bunkr,
    "pixeldrain": crawlers.Pixeldrain,
}


def get_crawler(url: URL, http_client: Requester) -> Crawler:
    crawler = _choice_crawler(url)
    if crawler is None:
        raise CrawlerNotFound(url)

    logger.debug("Received <%s> crawler for %s", crawler.__module__, url)
    return crawler(http_client)


def _choice_crawler(url: URL) -> type[Crawler] | None:
    if url.host is None:
        return None

    key = next((key for key in MAPPING.keys() if key in url.host), None)
    if key is None:
        return None

    return MAPPING[key]
