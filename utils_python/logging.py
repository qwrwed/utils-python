import logging
from contextlib import contextmanager
from typing import Optional as Opt
from typing import Type

LOG_DATEFMT = "%Y-%m-%dT%H:%M:%S"
LOG_FORMAT = "%(asctime)s.%(msecs)03d %(filename)s:%(lineno)s %(levelname)s %(name)s %(funcName)s(): %(message)s"


def setup_logging():
    """
    sets up root logger, e.g. `logging.info("test")`
    """
    setup_logger()


def setup_logger(
    name="",
    format=LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    level=logging.INFO,
    handler_class: Type[logging.Handler] = logging.StreamHandler,
):
    """
    sets up and returns a configurable logger, e.g. `LOGGER.info("test")`
    """
    logger = logging.getLogger(name)

    formatter = logging.Formatter(fmt=format, datefmt=datefmt)

    handler = handler_class()
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.setLevel(level)

    return logger


@contextmanager
def logPrefixFilter(logger: logging.Logger, msg_prefix: str = ""):
    """
    Temporarily prepends logged messages with the given string.

    Args:
        logger: logger to prepend msg_prefix to.
        msg_prefix: string to prepend to logged messages.
    """

    def _filter(record: logging.LogRecord):
        record.msg = str(msg_prefix) + record.msg
        return record

    try:
        logger.addFilter(_filter)
        yield
    finally:
        logger.removeFilter(_filter)
