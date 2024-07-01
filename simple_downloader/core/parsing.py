from re import compile
from typing import Iterator, Optional

from bs4 import BeautifulSoup, NavigableString, Tag
from yarl import URL

from simple_downloader.core.exceptions import (
    ExtensionNotFoundError,
    FileTableNotFoundError,
    HyperlinkNotFoundError,
    ParsingError,
    TitleNotFoundError,
)
from simple_downloader.core.models import Extension, Filename
from simple_downloader.core.utils import decode_cloudflare_email_protection, sanitize


FILENAME = compile(r"(.*)(\.\w+$)")


def get_soup(html_page: str, parser: str = "lxml") -> BeautifulSoup:
    return BeautifulSoup(html_page, parser)


def parse_title(soup: BeautifulSoup) -> str:
    """Title parsing, considering the protection of emails from CloudFlare (sometimes used in filenames)."""

    def has_cloudflare_protection(tag: Tag) -> bool:
        return tag.select_one(".__cf_email__") is not None

    def parse_title_from_h1_with_cloudflare_protection(tag: Tag) -> str:
        match tag.next:
            case Tag() as tag_with_protection:  # title is completely consistent with the email
                return decode(tag_with_protection)
            case NavigableString() as html_string:  # first is a str, and the second is encoded
                tag_with_protection: Tag = html_string.next  # type: ignore[reportArgumentType]
                return f"{html_string.get_text(strip=True)}{decode(tag_with_protection)}"
            case _:
                raise ParsingError

    def decode(tag_with_protection: Tag) -> str:
        encoded_data: str = tag_with_protection["data-cfemail"]  # type: ignore[reportAssignmentType]
        return decode_cloudflare_email_protection(encoded_data)

    h1_tag: Tag | None = soup.h1
    if h1_tag is None:
        raise TitleNotFoundError

    if has_cloudflare_protection(h1_tag):
        return parse_title_from_h1_with_cloudflare_protection(h1_tag)

    return h1_tag.get_text(strip=True)


def parse_download_hyperlink(soup: BeautifulSoup) -> URL:
    """Return the URL from a hyperlink named "Download"."""

    tag_with_hyperlink = soup.find("a", href=True, string=compile(r"(?i)download"))
    if tag_with_hyperlink is None:
        raise HyperlinkNotFoundError("Download")

    return URL(tag_with_hyperlink["href"])  # type: ignore[reportArgumentType]


def parse_file_urls(
    soup: BeautifulSoup,
    file_table_selector: str,
    base_url: Optional[URL] = None,
) -> Iterator[URL]:
    """Parses file URLs from the album page using selectors from SoupSieve built into BeautifulSoup."""

    tags_with_file_urls = soup.select(file_table_selector)
    if not tags_with_file_urls:
        raise FileTableNotFoundError

    for tag in tags_with_file_urls:
        yield URL(tag["href"]) if base_url is None else URL(base_url.with_path(tag["href"]))  # type: ignore[reportArgumentType]


def parse_filename(name: str) -> Filename:
    match = FILENAME.search(name)
    if match is not None:
        stem, ext = match.groups()
        return Filename(sanitize(stem), Extension(ext))

    raise ExtensionNotFoundError(name)
