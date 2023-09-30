import json
from copy import deepcopy


def flatten(l: list[list]):
    return [item for sublist in l for item in sublist]


def deduplicate(l: list):
    l_deduplicated = []
    for item in l:
        if item not in l_deduplicated:
            l_deduplicated.append(item)
    return l_deduplicated


def serialize_data(data: any, indent=4, default=str):
    if isinstance(data, str):
        data_str = data
    else:
        try:
            data_str = json.dumps(data, indent=indent, default=default)
        except TypeError:
            data_str = json.dumps(stringify_keys(data), indent=indent, default=default)
    return data_str


def dump_data(data: any, filepath="tmp.json"):
    data_str = serialize_data(data)
    with open(filepath, "w+") as f:
        f.write(data_str)


def stringify_keys(d: dict):
    """
    Convert a dict's keys to strings if they are not.
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
