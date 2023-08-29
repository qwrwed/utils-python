import logging

from tqdm import tqdm

from .logging import setup_logger
from .typing import copy_signature


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
