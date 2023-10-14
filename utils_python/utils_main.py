import json
import logging
import platform
import sys
import time
import urllib.request
from urllib.error import HTTPError

LOGGER = logging.getLogger(__name__)


def noop(*_args, **_kwargs):
    pass


def identity(e):
    return e


def get_platform() -> str:
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


def make_get_request_to_url(url: str, src_key: str | None = None):
    LOGGER.debug(f"making GET request to {url}")
    last_request = last_requests.get(src_key)
    # TODO: remove src_key, get website from url instead
    if last_request is not None and time.time() - last_request <= 1:
        time.sleep(1)
    while True:
        try:
            last_requests[src_key] = time.time()
            req = urllib.request.Request(url)
            req.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7",
            )
            with urllib.request.urlopen(req) as url_open:
                res_bytes = url_open.read()
            break
        except HTTPError as exc:
            if exc.code == 429:  # TOO_MANY_REQUESTS
                time.sleep(1)
                continue
            if exc.code == 404:  # NOT_FOUND
                return None
            LOGGER.info(
                f"unhandled HTTP error code={exc.code!r} msg={exc.msg!r} url={exc.url!r}"
            )
            breakpoint()
            return None
    res_str = res_bytes.decode()
    try:
        return json.loads(res_str)
    except json.decoder.JSONDecodeError:
        return res_str
