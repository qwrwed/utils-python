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


def dump_data(data: any, filepath="tmp.json"):
    if isinstance(data, str):
        data_str = data
    else:
        indent = 4
        try:
            data_str = json.dumps(data, indent=indent)
        except TypeError:
            data_str = json.dumps(stringify_keys(data), indent=indent)
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
