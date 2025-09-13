from pathlib import Path

from mutagen.easymp4 import EasyMP4, EasyMP4Tags

from utils_python.utils_typing import PathInput


def get_registered_keys() -> set[str]:
    return EasyMP4.Get.keys() & EasyMP4.Set.keys() & EasyMP4.Delete.keys()


def set_tag_mp4_text(
    filepath: PathInput,
    key: str,
    value: str | list[str],
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
    default=None,
    required=False,
):
    filepath = Path(filepath)
    key = key.lower()
    if not key in get_registered_keys():
        EasyMP4Tags.RegisterFreeformKey(key, key.upper())
    mp4 = EasyMP4(filepath)
    if key in mp4 and mp4[key] != []:
        [value] = mp4[key]
    else:
        if required:
            raise KeyError(key)
        value = default
    return value

def get_tag_mp4_text_multi(
    filepath: PathInput,
    key: str,
    default=None,
    required=False,
):
    if default is None:
        default = []
    filepath = Path(filepath)
    key = key.lower()
    if not key in get_registered_keys():
        EasyMP4Tags.RegisterFreeformKey(key, key.upper())
    mp4 = EasyMP4(filepath)
    if key in mp4:
        value = mp4[key]
    else:
        if required:
            raise KeyError(key)
        value = default
    return value
