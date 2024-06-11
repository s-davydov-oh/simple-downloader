class CrawlerNotFoundError(Exception):
    """No crawler was found for the hosting"""


class ExtensionNotFound(Exception):
    """The file doesn't have an extension."""


class InvalidContentType(Exception):
    """The server returned an empty "content-type"."""
