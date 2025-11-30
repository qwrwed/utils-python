from utils_python.utils_media.id3 import ensure_key_registered_id3_txxx
from utils_python.utils_media.mp4 import ensure_key_registered_mp4_freeform


def ensure_key_registered(
    key: str,
    desc_id3: str | None = None,
    name_mp4: str | None = None,
    mean_mp4: str = "com.apple.iTunes",
) -> None:
    ensure_key_registered_id3_txxx(key, desc_id3)
    ensure_key_registered_mp4_freeform(key, name_mp4, mean_mp4)
