import json
from pathlib import Path
import tempfile
import unittest

from tools import unified


class UnifiedPlanTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.scan = self.base / "scan"
        self.scan.mkdir()
        (self.scan / "scan.json").write_text(json.dumps({
            "device": {"model": "MiTV-MZTU1", "device": "mztu1", "product": "mztu1",
                       "release": "14", "sdk": "34", "build_id": "TEST"},
            "installed": ["com.example.keep", "com.example.one", "com.example.two"],
            "disabled": ["com.example.two"],
            "home": "com.google.android.apps.tv.launcherx/.MainActivity",
            "setupwraith_owns_wifi": False,
            "adb_secure": "1",
        }), encoding="utf-8")
        self.reference = self.base / "reference.txt"
        self.reference.write_text("com.example.one\ncom.example.two\n", encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def test_exact_model_and_candidates(self):
        data = json.loads((self.scan / "scan.json").read_text())
        self.assertTrue(unified.exact_mztu1(data["device"]))
        self.assertEqual(unified.candidates(["com.example.one", "com.example.two"],
                                            data["installed"], data["disabled"],
                                            ["com.example.one"]), [])

    def test_plan_is_review_only_until_explicitly_approved(self):
        out = self.base / "plan.txt"
        unified.write_plan(self.scan, out, self.reference, [], [], False)
        text = out.read_text()
        self.assertIn("# candidate: com.example.one", text)
        self.assertNotIn("\ncom.example.one\n", text)

    def test_plan_can_approve_one_package(self):
        out = self.base / "plan.txt"
        unified.write_plan(self.scan, out, self.reference, [], ["com.example.one"], False)
        self.assertEqual(unified.recovery.read_list(out), ["com.example.one"])

    def test_neighbor_profile_needs_explicit_mismatch_ack(self):
        original = unified.DEFAULT_REFERENCE
        unified.DEFAULT_REFERENCE = self.reference
        self.addCleanup(setattr, unified, "DEFAULT_REFERENCE", original)
        with self.assertRaises(SystemExit):
            unified.write_plan(self.scan, self.base / "plan.txt", self.reference, [],
                               ["com.example.one"], False)

    def test_config_is_small_and_launcher_compatible(self):
        out = self.base / "theme"
        unified.write_config(out, ["com.example.keep"], ["190:com.example.keep"], 6)
        self.assertEqual(json.loads((out / "config.json").read_text()), {
            "columns": 6, "dock_apps": ["com.example.keep"], "app_keys": ["190:com.example.keep"]
        })

    def test_brand_scope_lists_android_profiles(self):
        self.assertIn("supported", unified.supported_platform_message("TCL"))


if __name__ == "__main__":
    unittest.main()
