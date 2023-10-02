import logging

LOGGER = logging.getLogger(__name__)


def str_upper(value):
    return str(value).upper()


def truncate_str(s: str, max_length: int, end="..."):
    if max_length <= len(end):
        raise ValueError(
            f"truncate_str(): {max_length=} must be greater than {len(end)=}"
        )
    if len(s) > max_length:
        return s[: max_length - len(end)] + end
    return s


def ensure_caps(s: str):
    """
    makes first letter of every word uppercase, but doesn't make anything else lowercase
    """
    if len(s) == 0:
        breakpoint()
        pass
    s_parts = []
    for s_part in s.split(" "):
        s_part_caps = s_part[0].upper()
        if len(s_part) > 1:
            s_part_caps += s_part[1:]
        s_parts.append(s_part_caps)
    s_caps = " ".join(s_parts)
    return s_caps
