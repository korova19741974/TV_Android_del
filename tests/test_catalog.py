import unittest

from tools import catalog


class CatalogTest(unittest.TestCase):
    def test_only_requested_profiles_are_allowed(self):
        self.assertEqual(catalog.SUPPORTED_BRANDS, ("Xiaomi",))
        self.assertTrue(catalog.is_supported_profile({
            "brand": "Xiaomi", "tv": "Xiaomi Mi Box S", "os": "Android TV 12"
        }))
        self.assertTrue(catalog.is_supported_profile({
            "brand": "Xiaomi", "tv": "Xiaomi TV A Pro", "os": "Google TV 14"
        }))
        self.assertFalse(catalog.is_supported_profile({
            "brand": "Xiaomi", "tv": "Xiaomi TV Stick 4K", "os": "Google TV 14"
        }))
        self.assertFalse(catalog.is_supported_profile({
            "brand": "TCL", "tv": "TCL 75C6K", "os": "Google TV 12"
        }))


if __name__ == "__main__":
    unittest.main()
