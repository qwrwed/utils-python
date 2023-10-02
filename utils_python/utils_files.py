import json
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional

from tqdm import tqdm

from .utils_data import deduplicate, serialize_data
from .utils_main import identity
from .utils_strings import truncate_str

LOGGER = logging.getLogger(__name__)


def dump_data(data: any, filepath="tmp.json", mode="w"):
    data_str = serialize_data(data)
    with open(filepath, mode) as f:
        f.write(data_str)


def run_on_path(
    path: Path,
    file_callback: Optional[Callable[[Path], Any]] = None,
    dir_callback: Optional[Callable[[Path], Any]] = None,
    depth=0,
):
    if not isinstance(path, Path):
        path = Path(path)
    path_results: dict[str, Any]
    if path.is_file():
        path_results = {"is_dir": False}
        if file_callback is not None:
            path_results["result"] = file_callback(path)
        return {path: path_results}
    if path.is_dir():
        path_results = {"is_dir": True}
        if dir_callback is not None:
            path_results["result"] = dir_callback(path)
        subpath_results: dict[Path, dict[str, Any]] = {}
        subpaths = list(path.iterdir())
        with tqdm(subpaths, leave=depth == 0) as pbar:
            for i, subpath in enumerate(pbar):
                pbar.set_description(str(subpath))
                subpath_dict = run_on_path(
                    subpath, file_callback, dir_callback, depth + 1
                )
                subpath_results.update(subpath_dict)
                if i == len(subpaths) - 1:
                    pbar.set_description(repr(path))
            pbar.set_description(repr(path))
        path_results["contents"] = subpath_results
        return {path: path_results}
    raise TypeError(f"{path=!r} was not a file or a dir")


def read_list_from_file(
    filepath: Path, element_fn=identity, deduplicate_list=True, optional=True
):
    if not filepath.is_file():
        if optional:
            return []
        raise FileNotFoundError(f"Tried to read from {filepath}, but it was not a file")

    with open(filepath) as f:
        file_lines_str = f.readlines()

    try:
        file_lines_list = json.loads(" ".join(file_lines_str))
        if not isinstance(file_lines_list, list):
            raise ValueError(
                f"Expected list from {filepath}, got {type(file_lines_list)}"
            )
    except json.decoder.JSONDecodeError:
        file_lines_list = [line.strip() for line in file_lines_str]

    if deduplicate_list:
        file_lines_list = deduplicate(file_lines_list)

    results = []
    for line in file_lines_list:
        try:
            result = element_fn(line)
        except TypeError as exc:
            raise TypeError(
                f"Failed to call {element_fn.__name__ or element_fn}({line})"
            ) from exc
        results.append(result)

    return results


def read_dict_from_file(
    filepath: Path, key_fn=identity, value_fn=identity, optional=True
):
    if not filepath.is_file():
        if optional:
            return {}
        raise FileNotFoundError(f"Tried to read from {filepath}, but it was not a file")

    with open(filepath) as f:
        file_contents = f.read()

    if not file_contents:
        return {}

    try:
        json_data = json.loads(file_contents)
    except json.decoder.JSONDecodeError as exc:
        raise ValueError(f"Could not load {filepath} as JSON") from exc
    if not isinstance(json_data, dict):
        raise ValueError(f"Expected dict from {filepath}, got {type(json_data)}")

    return {key_fn(key): value_fn(value) for key, value in json_data.items()}


@contextmanager
def write_at_exit(
    obj,
    filepath: Path | str | None,
    indent: int | None = 4,
    overwrite: bool = False,
    default_encode: Callable = str,
    no_warning=False,
):
    if filepath is None:
        yield
        return

    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    if not filepath.parent.is_dir():
        raise NotADirectoryError(filepath)

    if filepath.exists():
        if overwrite:
            if not no_warning:
                LOGGER.warning("file '%s' exists and will be overwritten", filepath)
        else:
            raise FileExistsError(filepath)
    LOGGER.info("will write %s to '%s'", type(obj), filepath)

    try:
        yield

    finally:
        obj_str = truncate_str(str(obj), 30)
        LOGGER.info(f"writing {obj_str} to {filepath}")
        dump_data(serialize_data(obj, indent=indent, default=default_encode), filepath)
