from __future__ import annotations

import logging
import platform
import sys
from typing import TypeVar


def noop(
    *_args: tuple[object],
    **_kwargs: dict[str, object],
):
    pass


_T = TypeVar("_T")


def identity(e: _T) -> _T:
    return e


def get_platform() -> str:
    if hasattr(sys, "getandroidapilevel"):
        return "android"
    return platform.system().lower()


def setup_excepthook(
    logger: logging.Logger,
    keyboardinterrupt_log_str,
):
    """sets up excepthook to handle uncaught exceptions"""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            if keyboardinterrupt_log_str:
                logger.info(keyboardinterrupt_log_str)
            else:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            logger.critical(
                "Exception occured:", exc_info=(exc_type, exc_value, exc_traceback)
            )

    sys.excepthook = handle_exception
