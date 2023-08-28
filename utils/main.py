import json


def flatten(l: list[list]):
    return [item for sublist in l for item in sublist]


def deduplicate(l: list):
    l_deduplicated = []
    for item in l:
        if item not in l_deduplicated:
            l_deduplicated.append(item)
    return l_deduplicated


def dump_data(data: any, filepath="tmp.json"):
    data_str = json.dumps(data, indent=4)
    with open(filepath, "w+") as f:
        f.write(data_str)
