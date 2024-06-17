from re import compile

from bs4 import BeautifulSoup, NavigableString, Tag
from yarl import URL

from simple_downloader.core.exceptions import DownloadHyperlinkNotFound, ParsingError, TitleNotFound
from simple_downloader.core.utils import decode_cloudflare_email_protection


def parse_title(soup: BeautifulSoup) -> str:
    """Takes into account the presence of email protection from cloudflare."""

    h1_tag: Tag | None = soup.h1
    if h1_tag is None:
        raise TitleNotFound

    if _has_cf_protection(h1_tag):
        return _parse_h1_with_cf_protection(h1_tag)

    return h1_tag.get_text(strip=True)


def _has_cf_protection(tag: Tag) -> bool:
    return tag.select_one(".__cf_email__") is not None


def _parse_h1_with_cf_protection(tag: Tag) -> str:
    def decode(tag_with_cf_protection: Tag) -> str:
        encoded_data: str = tag_with_cf_protection["data-cfemail"]  # type: ignore[reportAssignmentType]
        return decode_cloudflare_email_protection(encoded_data)

    match tag.next:
        case Tag() as a_tag_with_cf_protection:
            return decode(a_tag_with_cf_protection)
        case NavigableString() as html_string:
            a_tag_with_cf_protection: Tag = html_string.next  # type: ignore[reportArgumentType]
            return f"{html_string.get_text(strip=True)}{decode(a_tag_with_cf_protection)}"
        case _:
            raise ParsingError


def parse_download_hyperlink(soup: BeautifulSoup) -> URL:
    """Return the URL from a hyperlink named "Download"."""

    a_tag_with_hyperlink = soup.find("a", href=True, string=compile(r"(?i)download"))
    if a_tag_with_hyperlink is None:
        raise DownloadHyperlinkNotFound

    return URL(a_tag_with_hyperlink["href"])  # type: ignore[reportArgumentType]
