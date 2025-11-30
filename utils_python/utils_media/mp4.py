from pathlib import Path

from mutagen.easymp4 import EasyMP4, EasyMP4Tags

from utils_python.utils_typing import PathInput


def get_registered_keys_mp4() -> set[str]:
    return EasyMP4.Get.keys() & EasyMP4.Set.keys() & EasyMP4.Delete.keys()


def ensure_key_registered_mp4_freeform(
    key: str,
    name: str | None = None,
    mean: str = "com.apple.iTunes",
) -> None:
    if name is None:
        name = key.upper()
    if not key in get_registered_keys_mp4():
        EasyMP4Tags.RegisterFreeformKey(key, name, mean)


def get_tag_text_mp4(
    filepath: PathInput,
    key: str,
    default: str | None = None,
    required: bool = False,
) -> str | None:
    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_mp4_freeform(key)
    mp4 = EasyMP4(filepath)
    if key in mp4 and mp4[key] != []:
        [value] = mp4[key]
    else:
        if required:
            raise KeyError(key)
        value = default
    return value


def set_tag_text_mp4(
    filepath: PathInput,
    key: str,
    value: str | list[str],
) -> None:

    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_mp4_freeform(key)
    mp4 = EasyMP4(filepath)
    mp4[key] = value
    mp4.save()


def del_tag_text_mp4(
    filepath: PathInput,
    key: str,
) -> None:
    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_mp4_freeform(key)
    mp4 = EasyMP4(filepath)
    if key in mp4:
        del mp4[key]
    mp4.save()


def get_tag_text_mp4_multi(
    filepath: PathInput,
    key: str,
    default: list[str] | None = None,
    required: bool = False,
) -> list[str]:
    if default is None:
        default = []
    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_mp4_freeform(key)
    mp4 = EasyMP4(filepath)
    if key in mp4:
        value = mp4[key]
    else:
        if required:
            raise KeyError(key)
        value = default
    return value
