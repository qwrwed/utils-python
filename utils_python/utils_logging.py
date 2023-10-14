from __future__ import annotations

import logging
from contextlib import contextmanager
from logging.config import fileConfig
from pathlib import Path
from typing import Type

LOG_DATEFMT = "%Y-%m-%dT%H:%M:%S"
LOG_FORMAT = "%(asctime)s.%(msecs)03d %(filename)s:%(lineno)s %(levelname)s %(name)s %(funcName)s(): %(message)s"


def setup_root_logger():
    """
    sets up root logger, e.g. `logging.info("test")`
    """
    setup_logger()


def setup_config_logging(config_path: Path | str) -> None:
    """
    sets up logging via fileConfig
    """
    if not isinstance(config_path, Path):
        config_path = Path(config_path)
    if not config_path.is_file():
        path = config_path if config_path.is_absolute() else config_path.resolve()
        raise FileNotFoundError(f"No such file or directory: '{path}")
    fileConfig(config_path, disable_existing_loggers=False)


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
    Temporarily prepends logged messages (if string) with the given string.

    Args:
        logger: logger to prepend msg_prefix to.
        msg_prefix: string to prepend to logged messages.
    """

    def _filter(record: logging.LogRecord):
        if isinstance(record.msg, str):
            record.msg = str(msg_prefix) + record.msg
        return record

    try:
        logger.addFilter(_filter)
        yield
    finally:
        logger.removeFilter(_filter)
