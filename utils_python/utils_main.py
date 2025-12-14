from __future__ import annotations

import logging
import platform
import sys
import time
from typing import Literal

import requests
from requests import Response

LOGGER = logging.getLogger(__name__)


def noop(*_args, **_kwargs):
    pass


def identity(e):
    return e


def get_platform() -> str:
    if hasattr(sys, "getandroidapilevel"):
        return "android"
    return platform.system().lower()


def setup_excepthook(logger: logging.Logger, keyboardinterrupt_log_str):
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


last_requests: dict[str | None, float] = {}


def make_get_request_to_url(
    url: str,
    src_key: str | None = None,
    min_delay: float | None = None,
    format: Literal["text", "json", "bytes", None] = "text",
    require_ok: bool = True,
    sleep_period_seconds: int = 5,
) -> str | dict[str, object] | list[object] | bytes | Response:
    LOGGER.debug(f"making GET request to {url}")
    last_request = last_requests.get(src_key)
    # TODO: remove src_key, get website from url instead
    if min_delay and last_request is not None and time.time() - last_request <= 1:
        time.sleep(min_delay)
    while True:
        last_requests[src_key] = time.time()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
        }
        response = requests.get(url, headers=headers)
        if response.ok:
            break
        if response.status_code == 429:  # TOO_MANY_REQUESTS
            time.sleep(1)
            continue
        response.raise_for_status()
    if format == "text":
        return response.text
    elif format == "json":
        return response.json()
    elif format == "bytes":
        return response.content
