from pathlib import Path
from utils_python.utils_typing import PathInput

from mutagen.easymp4 import EasyMP4
from mutagen.mp4 import MP4FreeForm


def register_custom_tag_mp4_text(
    key: str,
    atomid: str | None = None,
):
    if atomid is None:
        atomid = f"----:com.apple.iTunes:{key.upper()}"
    EasyMP4.RegisterTextKey(key, atomid)


def set_custom_tag_mp4_text(
    filepath: PathInput,
    key: str,
    value: str,
    *,
    atomid: str | None = None,
):
    filepath = Path(filepath)
    register_custom_tag_mp4_text(key, atomid)
    value_encoded = MP4FreeForm(value.encode())
    mp4 = EasyMP4(filepath)
    mp4[key] = value_encoded
    mp4.save()

def get_custom_tag_mp4_text(
    filepath: PathInput,
    key: str,
    *,
    atomid: str | None = None,
):
    filepath = Path(filepath)
    register_custom_tag_mp4_text(key, atomid)
    mp4 = EasyMP4(filepath)
    [value_encoded] = mp4[key]
    return value_encoded.decode()
