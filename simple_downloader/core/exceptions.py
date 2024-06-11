class CrawlerNotFoundError(Exception):
    """No crawler was found for the hosting"""


class ExtensionNotSupported(Exception):
    """The extension is not in the list of "supported extensions"."""
