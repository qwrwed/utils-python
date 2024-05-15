from __future__ import annotations

import json
import logging
from copy import deepcopy
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)


def flatten(l: list[list]):
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
        excluded_types = (str)
    return isinstance(obj, Iterable) and not isinstance(obj, excluded_types)


def stringify_keys(d: dict):
    """
    Convert a dict's keys to strings if they are not already.
    https://stackoverflow.com/a/51051641
    """
    d_copy = deepcopy(d)
    for key in d.keys():
        # check inner dict
        if isinstance(d[key], dict):
            value = stringify_keys(d[key])
        else:
            value = d[key]

        # convert nonstring to string if needed
        if not isinstance(key, str):
            try:
                d_copy[str(key)] = value
            except Exception:
                try:
                    d_copy[repr(key)] = value
                except Exception:
                    raise

            # delete old key
            del d_copy[key]
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
