from simple_downloader.config import BASE_DIR


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} | {levelname} | {name}.{funcName}:{lineno} - {message}",
            "datefmt": "%H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": BASE_DIR.joinpath("log.log"),
            "when": "midnight",
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "simple_downloader": {
            "level": "WARNING",
            "handlers": [
                "file",
            ],
        },
    },
}
