from __future__ import annotations

import json
import logging
import os
import shutil
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable, Optional
from zipfile import ZipFile

import requests
from tqdm import tqdm

from utils_python.utils_typing import PathInput

from .utils_data import deduplicate, serialize_data
from .utils_main import identity
from .utils_strings import truncate_str

LOGGER = logging.getLogger(__name__)


def dump_data(
    data: any,
    filepath: PathInput = "tmp.json",
    mode="w",
):
    data_str = serialize_data(data)
    with open(filepath, mode) as f:
        f.write(data_str)


def run_on_paths(
    paths: list[Path],
    file_callback: Optional[Callable[[Path], Any]] = None,
    dir_callback: Optional[Callable[[Path], Any]] = None,
    depth=0,
):
    results = {}
    for path in (pbar := tqdm(paths, leave=depth == 0)):
        pbar.set_description(str(path))
        path_dict = run_on_path(path, file_callback, dir_callback, depth + 1)
        results.update(path_dict)
    return results


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
    filepath: PathInput,
    element_fn=identity,
    deduplicate_list=True,
    optional=True,
):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
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
    filepath: PathInput,
    key_fn=identity,
    value_fn=identity,
    optional=True,
):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
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
    filepath: PathInput | None,
    indent: int | None = 4,
    overwrite: bool = False,
    default_encode: Callable = str,
    write_empty=False,
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
        if obj or write_empty:
            obj_str = truncate_str(str(obj), 30)
            LOGGER.info(f"Writing {type(obj)} {obj_str} to {filepath}")
            dump_data(
                serialize_data(obj, indent=indent, default=default_encode), filepath
            )
        elif overwrite and filepath.is_file():
            LOGGER.info(
                f"Removing {filepath} as it is write_empty is False, but overwrite is True"
            )
            filepath.unlink()
        else:
            LOGGER.info(
                f"Not writing {type(obj)} to {filepath} as it is empty and write_if_empty is False"
            )


def make_parent_dir(filepath: str | Path):
    Path(filepath).parent.mkdir(exist_ok=True, parents=True)


def download(url, filepath, verbose=True):
    """
    Download URL to filepath
    """
    # https://stackoverflow.com/a/63831344

    if verbose:
        LOGGER.info(f"Downloading {url} to {filepath}")

    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        r.raise_for_status()  # Will only raise for 4xx codes, so...
        raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
    file_size = int(r.headers.get("Content-Length", 0))

    path = Path(filepath).expanduser().resolve()
    make_parent_dir(path)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    r.raw.read = partial(r.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
        with path.open("wb") as f:
            shutil.copyfileobj(r_raw, f)

    return path


def unzip(
    zipped_file: PathInput,
    class_=ZipFile,
    extract_dir: PathInput | None = None,
):
    if extract_dir is not None:
        extract_dir = Path(extract_dir)

    with class_(Path(zipped_file), "r") as zip_ref:
        zip_ref.extractall(extract_dir)


@contextmanager
def cd(newdir):
    # https://stackoverflow.com/a/24176022
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
