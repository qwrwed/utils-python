from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3

from utils_python.utils_typing import PathInput


def get_registered_keys_id3() -> set[str]:
    return EasyID3.Get.keys() & EasyID3.Set.keys() & EasyID3.Delete.keys()


def ensure_key_registered_id3_txxx(
    key: str,
    desc: str | None = None,
) -> None:
    if desc is None:
        desc = key.upper()
    if not key in get_registered_keys_id3():
        EasyID3.RegisterTXXXKey(key, desc)


def get_tag_text_id3(
    filepath: PathInput,
    key: str,
    default: str | None = None,
    required: bool = False,
) -> str | None:
    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_id3_txxx(key)
    id3 = EasyID3(filepath)
    if key in id3 and id3[key] != []:
        [value] = id3[key]
    else:
        if required:
            raise KeyError(key)
        value = default
    return value


def set_tag_text_id3(
    filepath: PathInput,
    key: str,
    value: str | list[str],
) -> None:
    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_id3_txxx(key)
    try:
        id3 = EasyID3(filepath)
    except ID3NoHeaderError:
        mp3 = MP3(filepath)
        mp3.add_tags(ID3=ID3)
        mp3.save()
        id3 = EasyID3(filepath)
    id3[key] = value
    id3.save()


def del_tag_text_id3(
    filepath: PathInput,
    key: str,
) -> None:
    filepath = Path(filepath)
    key = key.lower()
    ensure_key_registered_id3_txxx(key)
    id3 = EasyID3(filepath)
    if key in id3:
        del id3[key]
    id3.save()
