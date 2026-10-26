import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POWERSHELL_INSTALLER = ROOT / "launcher" / "build-and-install.ps1"


class PowerShellLauncherInstallerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = POWERSHELL_INSTALLER.read_text(encoding="utf-8-sig")

    def test_checks_tv_sdk_before_building(self):
        sdk_check = self.script.index("getprop ro.build.version.sdk")
        gradle_build = self.script.index(".\\gradlew.bat assembleRelease")
        self.assertLess(sdk_check, gradle_build)
        self.assertIn("INSTALL_FAILED_OLDER_SDK", self.script)
        self.assertIn("$tvSdkExit = $LASTEXITCODE", self.script)
        self.assertIn("if ($tvSdkExit -ne 0 -or -not $tvSdkLine)", self.script)

    def test_validates_launcher_before_setting_home(self):
        launcher_start = self.script.index("am start -W -a android.intent.action.MAIN")
        set_home = self.script.index(
            "cmd package set-home-activity --user 0 com.gathin.tvhome/.MainActivity"
        )
        self.assertLess(launcher_start, set_home)

    def test_recovery_instructions_use_selected_python_runtime(self):
        recovery_block = self.script[self.script.index("function Undo-Handover") :]
        self.assertIn("$recoveryPython", recovery_block)
        self.assertNotIn(
            '"tools\\venv\\Scripts\\python.exe tools\\tv.py', recovery_block
        )

    def test_local_properties_uses_forward_slashes(self):
        self.assertIn("$sdk -replace '\\\\', '/'", self.script)


if __name__ == "__main__":
    unittest.main()
