from __future__ import annotations

import logging
from pathlib import Path

import requests
from tqdm import tqdm

from .utils_logging import setup_logger
from .utils_typing import PathInput, copy_signature

LOGGER = logging.getLogger(__name__)


class TqdmLoggingHandler(logging.StreamHandler):
    # https://stackoverflow.com/a/67257516
    """Avoid tqdm progress bar interruption by logger's output to console"""
    # see logging.StreamHandler.eval method:
    # https://github.com/python/cpython/blob/d2e2534751fd675c4d5d3adc208bf4fc984da7bf/Lib/logging/__init__.py#L1082-L1091
    # and tqdm.write method:
    # https://github.com/tqdm/tqdm/blob/f86104a1f30c38e6f80bfd8fb16d5fcde1e7749f/tqdm/std.py#L614-L620

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg, end=self.terminator)
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


@copy_signature(setup_logger)
def setup_tqdm_logger(*args, **kwargs):
    assert (
        kwargs.get("handler_class") is None
    ), "setup_tqdm_logger uses its own handler_class; use setup_logger if you wish to specify it"
    return setup_logger(*args, **kwargs, handler_class=TqdmLoggingHandler)


@copy_signature(print)
def print_tqdm(*args, **kwargs):
    if "flush" in kwargs:
        del kwargs["flush"]
    sep = kwargs.get("sep", " ")
    s = sep.join((str(arg) for arg in args))
    tqdm.write(s, **kwargs)


def download_tqdm(
    url: str,
    filepath: PathInput,
    position: int | None = None,
    leave: bool = False,
) -> None:
    # https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests/37573701#37573701
    filepath = Path(filepath)

    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)

    # Sizes in bytes.
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    filepath.parent.mkdir(exist_ok=True, parents=True)
    with tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        position=position,
        leave=leave,
    ) as progress_bar:
        with open(filepath, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

    if total_size != 0 and progress_bar.n != total_size:
        raise RuntimeError("Could not download file")
