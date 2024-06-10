class CrawlerNotFoundError(Exception):
    """No crawler was found for the hosting"""


class InvalidContentTypeError(Exception):
    """The server returned an empty “content-type”"""
