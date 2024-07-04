from logging import getLogger
from re import compile

from yarl import URL

from simple_downloader import crawlers
from simple_downloader.core.exceptions import CrawlerNotFound
from simple_downloader.core.models import Crawler
from simple_downloader.handlers.requester import Requester


logger = getLogger(__name__)

HOST_MAPPING = {
    compile(r"cyberdrop"): crawlers.Cyberdrop,
    compile(r"bunkr"): crawlers.Bunkr,
}


def get_crawler(url: URL, http_client: Requester) -> Crawler:
    crawler = _choice_crawler(url)
    return crawler(url.origin(), http_client)


def _choice_crawler(url: URL) -> type[Crawler]:
    if url.host is not None:
        for host_pattern, crawler in HOST_MAPPING.items():
            if host_pattern.search(url.host):
                logger.debug("Received <%s> crawler for %s", crawler.__module__, url)
                return crawler

    raise CrawlerNotFound(url)
