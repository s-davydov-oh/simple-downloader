from simple_downloader.config import BASE_DIR


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} | {levelname} | {module}:{funcName}:{lineno} - {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR.joinpath("debug.log"),
            "formatter": "default",
        },
    },
    "loggers": {
        "simple_downloader": {
            "level": "DEBUG",
            "handlers": ["file"],
        },
    },
}
