from __future__ import annotations

import json
import logging
from copy import deepcopy
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)


def flatten(l: list[list[object]]) -> list[object]:
    return [item for sublist in l for item in sublist]


def sort_dict(d, sortkey=lambda x: x):
    return {key: dict(sorted(d[key].items(), key=sortkey)) for key in sorted(d)}


def deduplicate(l: list):
    l_deduplicated = []
    for item in l:
        if item not in l_deduplicated:
            l_deduplicated.append(item)
    return l_deduplicated


def is_iterable(obj, excluded_types=None):
    if excluded_types is None:
        excluded_types = (str,)
    return isinstance(obj, Iterable) and not isinstance(obj, excluded_types)


def stringify_keys(d: dict):
    """
    Convert a dict's keys to strings if they are not already.
    """
    d_copy = {}
    for key, value in d.items():
        # Convert non-string keys to strings
        if not isinstance(key, str):
            try:
                key = str(key)
            except Exception:
                key = repr(key)

        # Recursively process nested dictionaries
        if isinstance(value, dict):
            value = stringify_keys(value)

        d_copy[key] = value

    return d_copy


def serialize_data(data: Any, indent=4, default=str):
    if isinstance(data, str):
        data_str = data
    else:
        try:
            data_str = json.dumps(data, indent=indent, default=default)
        except TypeError:
            data_str = json.dumps(stringify_keys(data), indent=indent, default=default)
    return data_str
