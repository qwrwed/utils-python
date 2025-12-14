import logging
import time
from typing import Literal, TypedDict, Unpack, overload

import requests

LOGGER = logging.getLogger(__name__)


last_requests: dict[str | None, float] = {}


class _BaseParams(TypedDict, total=False):
    src_key: str | None
    min_delay: float | None
    require_ok: bool
    sleep_period_seconds: int


class _TextParams(_BaseParams):
    format: Literal["text"]


class _JsonParams(_BaseParams):
    format: Literal["json"]


class _BytesParams(_BaseParams):
    format: Literal["bytes"]


class _NoneParams(_BaseParams):
    format: Literal[None]


@overload
def make_get_request_to_url(url: str) -> str: ...


@overload
def make_get_request_to_url(
    url: str,
    **params: Unpack[_TextParams],
) -> str: ...


@overload
def make_get_request_to_url(
    url: str,
    **params: Unpack[_JsonParams],
) -> dict[str, object] | list[object]: ...


@overload
def make_get_request_to_url(
    url: str,
    **params: Unpack[_BytesParams],
) -> bytes: ...


@overload
def make_get_request_to_url(
    url: str,
    **params: Unpack[_NoneParams],
) -> requests.Response: ...


def make_get_request_to_url(
    url: str,
    *,
    src_key: str | None = None,
    min_delay: float | None = None,
    format: Literal["text", "json", "bytes", None] = "text",
    require_ok: bool = True,
    sleep_period_seconds: int = 5,
) -> str | dict[str, object] | list[object] | bytes | requests.Response:
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
        if response.status_code == 429:  # TOO_MANY_REQUESTS
            LOGGER.warning(response.status_code)
            breakpoint()
            time.sleep(sleep_period_seconds)
            continue
        if response.ok or not require_ok:
            break
        response.raise_for_status()
    if format == "text":
        return response.text
    elif format == "json":
        json_data: dict[str, object] | list[object] = response.json()
        return json_data
    elif format == "bytes":
        return response.content
    elif format is None:
        return response
