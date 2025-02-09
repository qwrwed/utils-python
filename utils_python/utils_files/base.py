from pathlib import Path

from utils_python.utils_typing import PathInput


def make_parent_dir(filepath: PathInput):
    Path(filepath).parent.mkdir(exist_ok=True, parents=True)
