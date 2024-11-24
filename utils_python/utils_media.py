from pathlib import Path

from mutagen.easymp4 import EasyMP4, EasyMP4Tags

from utils_python.utils_typing import PathInput


def get_registered_keys() -> set[str]:
    return EasyMP4.Get.keys() & EasyMP4.Set.keys() & EasyMP4.Delete.keys()


def set_tag_mp4_text(
    filepath: PathInput,
    key: str,
    value: str,
):

    filepath = Path(filepath)
    key = key.lower()
    if not key in get_registered_keys():
        EasyMP4Tags.RegisterFreeformKey(key, key.upper())
    mp4 = EasyMP4(filepath)
    mp4[key] = value
    mp4.save()


def get_tag_mp4_text(
    filepath: PathInput,
    key: str,
):
    filepath = Path(filepath)
    key = key.lower()
    if not key in get_registered_keys():
        EasyMP4Tags.RegisterFreeformKey(key, key.upper())
    mp4 = EasyMP4(filepath)
    [value] = mp4[key]
    return value
