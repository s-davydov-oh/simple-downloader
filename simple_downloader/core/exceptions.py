class CrawlerNotFound(Exception):
    """No crawler was found for the hosting."""


class ExtensionNotFound(Exception):
    """The file doesn't have an extension."""


class ExtensionNotSupported(Exception):
    """The extension is not in the list of "supported extensions"."""


class InvalidContentType(Exception):
    """The server returned an empty "content-type"."""


class InvalidMediaType(Exception):
    """Crawler can't identify the media type."""


class ParsingError(Exception):
    """Probably a parsing problem with the Crawler."""
