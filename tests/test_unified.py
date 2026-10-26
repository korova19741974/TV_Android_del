import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_launcher_apps_can_be_selected_by_number(self):
        apps = unified.launchable_from("com.example.one/.MainActivity\ncom.example.two/.MainActivity\n",
                                       ["com.example.keep", "com.example.one", "com.example.two"])
        self.assertEqual(apps, ["com.example.one", "com.example.two"])
        self.assertEqual(unified.selected_apps(apps, "2,1,2"), ["com.example.two", "com.example.one"])
        with self.assertRaises(SystemExit):
            unified.selected_apps(apps, "3")

    def test_config_accepts_a_hold_sleep_key(self):
        out = self.base / "theme"
        unified.write_config(out, ["com.example.keep"], ["hold:183:sleep"], 6, "#101820")
        config = json.loads((out / "config.json").read_text())
        self.assertEqual(config["background_color"], "#101820")
        self.assertEqual(config["app_keys"], ["hold:183:sleep"])

    def test_config_accepts_simple_widgets(self):
        out = self.base / "widget-theme"
        unified.write_config(out, ["com.example.keep"], [], 6, "#101820", False, True, "Moscow", True)
        config = json.loads((out / "config.json").read_text())
        self.assertFalse(config["show_time"])
        self.assertTrue(config["show_date"])
        self.assertEqual(config["weather_city"], "Moscow")
        self.assertTrue(config["auto_sort_dock"])

    def test_empty_weather_city_is_written_as_hidden_widget(self):
        out = self.base / "no-weather-theme"
        unified.write_config(out, ["com.example.keep"], [], 6, weather_city="")
        self.assertEqual(json.loads((out / "config.json").read_text())["weather_city"], "")

    def test_learned_remote_key_result_is_read_without_manual_code(self):
        self.assertEqual(unified.parse_learned_key(
            "keycode=207 scancode=0 name=KEYCODE_NETFLIX\n"
        ), {"keycode": 207, "scancode": 0, "name": "KEYCODE_NETFLIX"})

    def test_learned_remote_key_result_rejects_incomplete_output(self):
        with self.assertRaises(ValueError):
            unified.parse_learned_key("button not found")

    def test_apk_install_rejects_non_apk_before_connecting(self):
        with self.assertRaises(SystemExit):
            unified.install_apk(self.base / "notes.txt")

    def test_apk_install_rejects_android_failure_output(self):
        apk = self.base / "broken.apk"
        apk.write_bytes(b"not a real apk")
        responses = [
            subprocess.CompletedProcess([], 0, "pushed", ""),
            subprocess.CompletedProcess([], 0, "Failure [INSTALL_FAILED_INVALID_APK]", ""),
            subprocess.CompletedProcess([], 0, "", ""),
        ]
        with mock.patch.object(unified.subprocess, "run", side_effect=responses):
            with self.assertRaisesRegex(SystemExit, "INSTALL_FAILED_INVALID_APK"):
                unified.install_apk(apk)

    def test_apk_install_accepts_android_success_output(self):
        apk = self.base / "valid.apk"
        apk.write_bytes(b"test fixture")
        responses = [
            subprocess.CompletedProcess([], 0, "pushed", ""),
            subprocess.CompletedProcess([], 0, "Success\n", ""),
            subprocess.CompletedProcess([], 0, "", ""),
        ]
        with mock.patch.object(unified.subprocess, "run", side_effect=responses) as run:
            self.assertEqual(unified.install_apk(apk), "Success")
        self.assertEqual(run.call_count, 3)

    def test_apk_install_rejects_mixed_success_and_failure_output(self):
        apk = self.base / "conflicting.apk"
        apk.write_bytes(b"test fixture")
        responses = [
            subprocess.CompletedProcess([], 0, "pushed", ""),
            subprocess.CompletedProcess([], 0, "Success\nFailure [INSTALL_FAILED_ABORTED]", ""),
            subprocess.CompletedProcess([], 0, "", ""),
        ]
        with mock.patch.object(unified.subprocess, "run", side_effect=responses):
            with self.assertRaisesRegex(SystemExit, "INSTALL_FAILED_ABORTED"):
                unified.install_apk(apk)

    def test_brand_scope_lists_only_xiaomi_profiles(self):
        self.assertIn("supported", unified.supported_platform_message("Xiaomi"))
        self.assertIn("Unsupported", unified.supported_platform_message("TCL"))


if __name__ == "__main__":
    unittest.main()
