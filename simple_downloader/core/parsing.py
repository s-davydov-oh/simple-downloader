from re import compile
from typing import Iterator, Optional

from bs4 import BeautifulSoup, NavigableString, Tag
from yarl import URL

from simple_downloader.core.exceptions import (
    DownloadHyperlinkNotFound,
    ExtensionNotFound,
    ParsingError,
    FileTableNotFound,
    TitleNotFound,
)
from simple_downloader.core.models import Extension, Filename
from simple_downloader.core.utils import decode_cloudflare_email_protection, sanitize


FILENAME = compile(r"(.*)(\.\w+$)")


def get_soup(html_page: str, parser: str = "lxml") -> BeautifulSoup:
    return BeautifulSoup(html_page, parser)


def parse_filename(name: str) -> Filename:
    match = FILENAME.search(name)
    if match is not None:
        stem, ext = match.groups()
        return Filename(sanitize(stem), Extension(ext))

    raise ExtensionNotFound(name)


def parse_title(soup: BeautifulSoup) -> str:
    """Takes into account the presence of email protection from cloudflare."""

    h1_tag: Tag | None = soup.h1
    if h1_tag is None:
        raise TitleNotFound

    if _has_cloudflare_protection(h1_tag):
        return _parse_title_from_h1_with_cloudflare_protection(h1_tag)

    return h1_tag.get_text(strip=True)


def _has_cloudflare_protection(tag: Tag) -> bool:
    return tag.select_one(".__cf_email__") is not None


def _parse_title_from_h1_with_cloudflare_protection(tag: Tag) -> str:
    """
    Cloudflare provides an obfuscation mechanism for email addresses, which is sometimes applied to filenames as well.

    The filename is either fully encrypted if the entire name falls under an email regular expression,
    or split into two parts, where the first will be a normal string and the second will be encrypted.
    """

    match tag.next:
        case Tag() as tag_with_protection:
            return _decode(tag_with_protection)
        case NavigableString() as html_string:
            tag_with_protection: Tag = html_string.next  # type: ignore[reportArgumentType]
            return f"{html_string.get_text(strip=True)}{_decode(tag_with_protection)}"
        case _:
            raise ParsingError


def _decode(tag_with_protection: Tag) -> str:
    encoded_data: str = tag_with_protection["data-cfemail"]  # type: ignore[reportAssignmentType]
    return decode_cloudflare_email_protection(encoded_data)


def parse_download_hyperlink(soup: BeautifulSoup) -> URL:
    """Return the URL from a hyperlink named "Download"."""

    tag_with_hyperlink = soup.find("a", href=True, string=compile(r"(?i)download"))
    if tag_with_hyperlink is None:
        raise DownloadHyperlinkNotFound

    return URL(tag_with_hyperlink["href"])  # type: ignore[reportArgumentType]


def parse_file_urls(
    soup: BeautifulSoup,
    file_table_selector: str,
    base_url: Optional[URL] = None,
) -> Iterator[URL]:
    """Parses file URLs from the album page using selectors from SoupSieve built into BeautifulSoup."""

    tags_with_file_urls = soup.select(file_table_selector)
    if not tags_with_file_urls:
        raise FileTableNotFound

    for tag in tags_with_file_urls:
        if base_url is not None:
            yield URL(base_url.with_path(tag["href"]))  # type: ignore[reportArgumentType]

        yield URL(tag["href"])  # type: ignore[reportArgumentType]
