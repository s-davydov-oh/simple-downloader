import logging.config

from simple_downloader.config import BASE_DIR


class ConsoleFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelname == "INFO"


class FileFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelname != "INFO"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_format": {
            "format": "{message}.",
            "style": "{",
        },
        "file_format": {
            "format": "{asctime} | {levelname} | {module}:{funcName}:{lineno} - {message}.",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "console_format",
            "filters": ["console_filter"],
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR.joinpath("debug.log"),
            "formatter": "file_format",
            "filters": ["file_filter"],
        },
    },
    "loggers": {
        "simple_downloader": {
            "level": "DEBUG",
            "handlers": ["file", "console"],
        },
    },
    "filters": {
        "console_filter": {
            "()": ConsoleFilter,
        },
        "file_filter": {
            "()": FileFilter,
        },
    },
}
