"""Profile scope for this compact Android TV-focused fork."""

import re

SUPPORTED_BRANDS = ("Xiaomi", "TCL")
TCL_DIAGONAL = re.compile(r'(?<!\d)(32|40|43|50|55|65|75|85|100)(?=(?:["″]|[A-Z]))')


def is_supported_profile(profile: dict) -> bool:
    """Whether a profile matches the requested brand, platform and model constraints."""
    brand = profile.get("brand")
    tv = profile.get("tv", "")
    os_name = profile.get("os", "")
    if not isinstance(brand, str) or not isinstance(tv, str) or not isinstance(os_name, str):
        return False
    if brand == "TCL":
        sizes = TCL_DIAGONAL.findall(tv)
        return not sizes or set(sizes) == {"75"}
    if brand == "Xiaomi":
        name = tv.casefold()
        is_box = "mi box" in name or "tv box" in name
        is_android_14_tv = (
            ("android 14" in os_name.casefold() or "google tv 14" in os_name.casefold())
            and "stick" not in name
            and "box" not in name
        )
        return is_box or is_android_14_tv
    return False
