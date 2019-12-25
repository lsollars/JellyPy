import sys
import logging
from logging.config import dictConfig


def log_setup(syslog="/dev/log"):
    """
    """
    logging_config = dict(
        version=1.0,
        formatters={
            "log_formatter": {
                "format": "{asctime} {name} {levelname}: {message}",
                "style": "{",
                "datefmt": r"%Y-%m-%d %H:%M:%S",
            }
        },
        handlers={
            "stream_handler": {
                "class": "logging.StreamHandler",
                "formatter": "log_formatter",
                "level": logging.DEBUG,
            },
            "syslog_handler": {
                "class": "logging.handlers.SysLogHandler",
                "formatter": "log_formatter",
                "level": logging.DEBUG,
                "address": syslog,
            },
        },
        root={"handlers": ["stream_handler", "syslog_handler"], "level": logging.DEBUG},
        disable_existing_loggers=False
    )
    dictConfig(logging_config)


if __name__ == "__main__":
    args = " ".join(sys.argv[1:])
    log_setup()
    logger = logging.getLogger("pylog")
    logger.debug(args)
    logger.info(args)
    logger.warning(args)
    logger.critical(args)
    logger.error(args)
