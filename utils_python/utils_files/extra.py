from __future__ import annotations

import json
import logging
import os
import shutil
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Callable, Generator, Optional
from zipfile import ZipFile

import requests
from filedate import File as FileDateObj
from tqdm import tqdm

from utils_python.utils_data import deduplicate, serialize_data
from utils_python.utils_files.base import make_parent_dir
from utils_python.utils_main import identity
from utils_python.utils_strings import truncate_str
from utils_python.utils_tqdm import print_tqdm
from utils_python.utils_typing import PathInput

LOGGER = logging.getLogger(__name__)


def dump_data(
    data: Any,
    filepath: PathInput = "tmp.json",
    mode="w",
    make_dir=True,
    rotate=False,
    encoding="utf-8",
):
    data_serialized = data if "b" in mode else serialize_data(data)
    if make_dir:
        make_parent_dir(filepath)
    if rotate:
        rotate_file(filepath)
    with open(filepath, mode, encoding=encoding) as f:
        f.write(data_serialized)


def rotate_file(
    filepath: PathInput,
    maximum_rotations: int | None = None,
    add_extension: str | None = None,
):
    orig_path = Path(filepath)
    if not orig_path.is_file():
        raise FileNotFoundError(orig_path)
    deletes: set[Path] = set()
    renames: dict[Path, Path] = {}
    i = 1
    src_path = orig_path
    while True:
        dest_stem = orig_path.stem + f".{i}"
        dest_suffix = orig_path.suffix
        if add_extension is not None:
            if not add_extension.startswith("."):
                add_extension = f".{add_extension}"
            dest_suffix += add_extension
        dest_path = orig_path.with_stem(dest_stem).with_suffix(dest_suffix)
        renames[src_path] = dest_path
        if (
            maximum_rotations is not None
            and i >= maximum_rotations
            and dest_path.is_file()
        ):
            deletes.add(dest_path)
        if not dest_path.is_file():
            break
        src_path = dest_path
        i += 1
    for path in deletes:
        path.unlink()
        if path in renames:
            del renames[path]
    for src_path, dest_path in reversed(renames.items()):
        src_path.rename(dest_path)


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


def run_on_path_flat(
    path: Path,
    file_callback: Optional[Callable[[Path], Any]] = None,
    dir_callback: Optional[Callable[[Path], Any]] = None,
):
    path = Path(path)
    all_results = {}
    for p in tqdm(list(path.rglob("*"))):
        if p.is_file():
            path_info = {"is_dir": False}
            if file_callback is not None:
                try:
                    path_result = file_callback(path)
                except Exception as exc:
                    print_tqdm(f"ERROR running callback on file {path!r}")
                    raise exc
                path_info["result"] = path_result
        elif p.is_dir():
            path_info = {"is_dir": True}
            if dir_callback is not None:
                try:
                    path_result = dir_callback(path)
                except Exception as exc:
                    print_tqdm(f"ERROR running callback on dir {path!r}")
                    raise exc
                path_info["result"] = path_result
        all_results[p] = path_info
    return all_results


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
            try:
                path_result = file_callback(path)
            except Exception as exc:
                print_tqdm(f"ERROR running callback on file {path!r}")
                raise exc
            path_results["result"] = path_result
        return {path: path_results}
    if path.is_dir():
        path_results = {"is_dir": True}
        if dir_callback is not None:
            try:
                dir_result = dir_callback(path)
            except Exception as exc:
                print_tqdm(f"ERROR running callback on dir {path!r}")
                raise exc
            path_results["result"] = dir_result
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
    encoding="utf-8",
):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not filepath.is_file():
        if optional:
            return []
        raise FileNotFoundError(f"Tried to read from {filepath}, but it was not a file")

    with open(filepath, encoding=encoding) as f:
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
    encoding="utf-8",
):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not filepath.is_file():
        if optional:
            return {}
        raise FileNotFoundError(f"Tried to read from {filepath}, but it was not a file")

    with open(filepath, encoding=encoding) as f:
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


@contextmanager
def preserve_filedate(
    filepath: Path,
    created=True,
    modified=True,
    accessed=False,
) -> Generator[None, None, None]:
    """
    Context manager which allows a file to be modified, recreated or accessed
     without changing the timestamp(s) associated with that file
    """
    file_date = FileDateObj(filepath)
    original_times = file_date.get().copy()

    if not created:
        del original_times["created"]
    if not modified:
        del original_times["modified"]
    if not accessed:
        del original_times["accessed"]

    yield
    new_times = {**file_date.get(), **original_times}
    file_date.set(**new_times)


def copy_filedate(
    file_from: Path,
    file_to: Path,
    created=True,
    modified=True,
    accessed=False,
):
    file_date_from = FileDateObj(file_from)
    original_times = file_date_from.get()

    if not created:
        del original_times["created"]
    if not modified:
        del original_times["modified"]
    if not accessed:
        del original_times["accessed"]

    file_date_to = FileDateObj(file_to)
    file_date_to.set(**original_times)


def update_filedate_created(
    filepath: Path,
    new_time: datetime,
) -> None:
    file_date = FileDateObj(filepath)
    file_date.created = new_time


def update_filedate_modified(
    filepath: Path,
    new_time: datetime,
) -> None:
    file_date = FileDateObj(filepath)
    file_date.modified = new_time


def update_filedate_accessed(
    filepath: Path,
    new_time: datetime,
) -> None:
    file_date = FileDateObj(filepath)
    file_date.accessed = new_time


def sanitize_filename_windows_style(name: str) -> str:
    # sanitizes filenames like Windows 10's "Create Shortcut" does
    s = ""
    for c in name:
        if c == "/":
            s += "-"
        elif c not in r"\:*?<>|":
            s += c
    return s


def create_windows_url_shortcut(
    url: str,
    path: PathInput,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.name.endswith(".url"):
        path = path.with_name(path.name + ".url")
    with open(path, "w", newline="\r\n") as f:
        f.write(f"[InternetShortcut]\nURL={url}")
