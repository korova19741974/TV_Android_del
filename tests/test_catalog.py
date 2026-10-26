import unittest

from tools import catalog


class CatalogTest(unittest.TestCase):
    def test_only_android_brands_have_profiles(self):
        self.assertEqual(catalog.SUPPORTED_BRANDS, ("Xiaomi", "Hisense", "TCL"))
        self.assertFalse(catalog.is_supported_profile("LG"))
        self.assertTrue(catalog.is_supported_profile("Xiaomi"))


if __name__ == "__main__":
    unittest.main()
