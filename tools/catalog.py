"""Brand scope for this compact Android TV-focused fork."""

SUPPORTED_BRANDS = ("Xiaomi", "Hisense", "TCL")


def is_supported_profile(brand: str, os_name: str = "") -> bool:
    """Whether a profile is for a selected Android TV or Google TV brand."""
    return brand in SUPPORTED_BRANDS
