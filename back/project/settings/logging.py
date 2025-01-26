import logging.config
import sys

import coloredlogs

try:
    from .settings_local import LOG_DATE_FMT
except Exception:
    LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

try:
    from .settings_local import NO_COLOR
except Exception:
    NO_COLOR = False

FMT = "%(asctime).19s • %(levelname).1s • %(name)s %(lineno)d • %(message)s"

if NO_COLOR:
    console_formater = "plainlogs"
else:
    console_formater = "coloredlogs"


def skip_static_requests(record):
    url = str(record.args[0])
    return not (url.startswith("GET /md/") or url.startswith("GET /st/"))


conf = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "coloredlogs": {
            "()": coloredlogs.ColoredFormatter,
            "fmt": FMT,
            "datefmt": LOG_DATE_FMT,
        },
        "plainlogs": {
            "format": FMT,
            "datefmt": LOG_DATE_FMT,
        },
        "verbose": {
            "format": FMT,
            "datefmt": LOG_DATE_FMT,
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": console_formater,
        },
    },
    "filters": {
        "skip_static_requests": {
            "()": "django.utils.log.CallbackFilter",
            "callback": skip_static_requests,
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": [
                "console",
            ],
            "propagate": False,
        },
        "django": {"level": "INFO", "handlers": ["console"], "propagate": False},
        # Set level to DEBUG and enable settings.DEBUG to see all SQL queries
        "django.db.backends": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        # Skip static and media files from runserver logs
        "django.server": {
            "level": "INFO",
            "filters": ["skip_static_requests"],
            "handlers": ["console"],
            "propagate": False,
        },
        # suppress DEBUG noise
        "sorl.thumbnail.base": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "PIL.TiffImagePlugin": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        # suppress DEBUG noise
        "django.utils.autoreload": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        # suppress DEBUG noise
        "urllib3.connectionpool": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
LOGGING_CONFIG = None
logging.config.dictConfig(conf)
