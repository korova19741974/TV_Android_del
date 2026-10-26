#!/usr/bin/env python3
"""The safe, single-entry workflow for a TV cleanup.

This is deliberately a coordinator, not a second ADB implementation:

    python tools/unified.py scan --out work/mztu1-scan
    python tools/unified.py plan --scan work/mztu1-scan --out work/mztu1-plan.txt
    python tools/unified.py config --out work/mztu1-theme --dock pkg.one,pkg.two --app-key 190:pkg.one
    TV_HOST=<tv ip> python tools/unified.py apply work/mztu1-plan.txt
    TV_HOST=<tv ip> python tools/unified.py restore work/mztu1-plan.txt
    TV_HOST=<tv ip> python tools/unified.py install --input-key-service --home-key-service

The default plan is review-only. Applying a reference list to a model that is not an exact match
requires an explicit --acknowledge-mismatch and explicit --approve package entries. The existing
disable/restore scripts remain the only code that changes packages on the TV.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PACKAGE_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+")
DEFAULT_REFERENCE = ROOT / "examples" / "xiaomi-tv-a-pro-2026" / "debloat.txt"
DEVICE_KEYS = (
    "model",
    "device",
    "product",
    "release",
    "sdk",
    "build_id",
)

sys.path.insert(0, str(TOOLS))
import recovery  # noqa: E402


def package_lines(text: str) -> list[str]:
    """Read package names from a list without allowing shell syntax through."""
    names = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        name = line.split()[0]
        if not PACKAGE_RE.fullmatch(name):
            raise ValueError(f"line {number}: not a package name: {name!r}")
        names.append(name)
    return names


def exact_mztu1(device: dict) -> bool:
    """MZTU1 is the only target for automatic Xiaomi guidance in this tool."""
    haystack = " ".join(str(device.get(key, "")) for key in ("model", "device", "product")).upper()
    return "MZTU1" in haystack


def candidates(reference_names: Iterable[str], installed: Iterable[str], disabled: Iterable[str],
               keep: Iterable[str]) -> list[str]:
    installed_set = set(installed)
    disabled_set = set(disabled)
    keep_set = set(keep)
    return [name for name in reference_names
            if name in installed_set and name not in disabled_set and name not in keep_set]


def run_tv(command: str) -> str:
    if not os.environ.get("TV_HOST"):
        raise SystemExit("set TV_HOST to the TV IP address")
    python = next((p for p in (TOOLS / "venv" / "bin" / "python",
                               TOOLS / "venv" / "Scripts" / "python.exe") if p.is_file()), None)
    if python is None:
        raise SystemExit("run: python -m venv tools/venv; tools/venv/Scripts/python.exe -m pip install -r tools/requirements.txt")
    result = subprocess.run([str(python), "-I", str(TOOLS / "tv.py"), command],
                            capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or
                         f"tv.py exited with status {result.returncode}")
    return result.stdout


def installed_from(text: str) -> list[str]:
    return [line.split(":", 1)[1].strip() for line in text.splitlines()
            if line.startswith("package:") and PACKAGE_RE.fullmatch(line.split(":", 1)[1].strip())]


def scan(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    props = {
        "model": run_tv("getprop ro.product.model").strip(),
        "device": run_tv("getprop ro.product.device").strip(),
        "product": run_tv("getprop ro.product.name").strip(),
        "release": run_tv("getprop ro.build.version.release").strip(),
        "sdk": run_tv("getprop ro.build.version.sdk").strip(),
        "build_id": run_tv("getprop ro.build.id").strip(),
    }
    installed = sorted(installed_from(run_tv("pm list packages -e --user 0")))
    disabled = sorted(installed_from(run_tv("pm list packages -d --user 0")))
    home = run_tv("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME").strip().splitlines()
    wifi = run_tv("dumpsys wifi")
    data = {
        "device": props,
        "installed": installed,
        "disabled": disabled,
        "home": next((line.strip() for line in reversed(home) if "/" in line), ""),
        "setupwraith_owns_wifi": (True if re.search(r"cname=\S*setupwraith", wifi)
                                   else False if "cname=" in wifi else None),
        "adb_secure": run_tv("getprop ro.adb.secure").strip(),
    }
    (out_dir / "scan.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"saved {out_dir / 'scan.json'}")
    print(f"model: {props['model'] or 'unknown'}; Android {props['release'] or '?'}; SDK {props['sdk'] or '?'}")
    print(f"installed: {len(installed)}; disabled: {len(disabled)}; Home: {data['home'] or 'unknown'}")
    if data["setupwraith_owns_wifi"] is True:
        print("WARNING: setupwraith appears to own the saved Wi-Fi network; do not disable it yet.")
    if data["adb_secure"] == "0":
        print("WARNING: ro.adb.secure=0; network ADB is unauthenticated until debugging is disabled.")
    return 0


def load_scan(path: Path) -> dict:
    try:
        data = json.loads((path / "scan.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"could not read {path / 'scan.json'}: {exc}")
    if not isinstance(data.get("device"), dict) or not isinstance(data.get("installed"), list):
        raise SystemExit(f"{path / 'scan.json'} is not a valid unified scan")
    return data


def write_plan(scan_dir: Path, out: Path, reference: Path, keep: list[str], approved: list[str],
               acknowledge_mismatch: bool) -> int:
    data = load_scan(scan_dir)
    reference_names = package_lines(reference.read_text(encoding="utf-8-sig"))
    installed = set(data["installed"])
    disabled = set(data.get("disabled", []))
    keep = list(dict.fromkeys(keep))
    for name in keep + approved:
        if not PACKAGE_RE.fullmatch(name):
            raise SystemExit(f"not a package name: {name!r}")
        if name not in installed:
            raise SystemExit(f"{name} is not installed for user 0; nothing was written")
    protected = recovery.core_packages(reference_names)
    if protected:
        raise SystemExit(f"reference list contains protected Android packages: {', '.join(protected)}")
    pool = candidates(reference_names, installed, disabled, keep)
    approved = list(dict.fromkeys(approved))
    unknown = [name for name in approved if name not in pool]
    if unknown:
        raise SystemExit("approved packages are not current, enabled candidates from the reference: " +
                         ", ".join(unknown))
    # There is no shipped MZTU1 package list yet. The default is the neighboring MZTU0 list, so even an
    # exact MZTU1 scan remains review-only unless the owner explicitly acknowledges that mismatch.
    exact = exact_mztu1(data["device"]) and reference.resolve() != DEFAULT_REFERENCE.resolve()
    if approved and not exact and not acknowledge_mismatch:
        raise SystemExit("the scan is not an exact MZTU1 profile; review the candidates, then repeat with "
                         "--acknowledge-mismatch and explicit --approve package names")
    lines = [
        "# Unified CleanYourTV plan. Only uncommented package lines are applied.",
        f"# Device: {data['device'].get('model', 'unknown')} / Android {data['device'].get('release', '?')} / SDK {data['device'].get('sdk', '?')}",
        f"# Reference: {reference}",
        "# Safety: disable-user only; no root and no uninstall. Undo with tools/unified.py restore <this file>.",
        "# Keep: " + (", ".join(keep) if keep else "none supplied"),
    ]
    if not exact:
        lines.append("# WARNING: this is not an exact MZTU1 package profile. Treat every candidate as review-only.")
    if data.get("setupwraith_owns_wifi") is True and "com.google.android.tungsten.setupwraith" in pool:
        lines.append("# WARNING: setupwraith owns Wi-Fi and was excluded automatically.")
        pool = [name for name in pool if name != "com.google.android.tungsten.setupwraith"]
        approved = [name for name in approved if name != "com.google.android.tungsten.setupwraith"]
    lines.append("")
    approved_set = set(approved)
    for name in pool:
        lines.append(name if name in approved_set else f"# candidate: {name}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {out}")
    print(f"candidates: {len(pool)}; approved: {len(approved)}; keep: {len(keep)}")
    if not approved:
        print("review-only plan: no TV changes can be made from this file yet")
    return 0


def write_config(out_dir: Path, dock: list[str], app_keys: list[str], columns: int) -> int:
    for name in dock:
        if not PACKAGE_RE.fullmatch(name):
            raise SystemExit(f"not a dock package name: {name!r}")
    for entry in app_keys:
        if not entry or "\n" in entry or "\r" in entry or ":" not in entry:
            raise SystemExit(f"invalid --app-key {entry!r}; use KEYCODE:package-or-action")
    if not 1 <= columns <= 8:
        raise SystemExit("--columns must be between 1 and 8")
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {"columns": columns, "dock_apps": dock, "app_keys": app_keys}
    path = out_dir / "config.json"
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"saved {path}; push it with tools/theme.sh {out_dir}")
    return 0


def script_command(action: str, list_path: Path) -> list[str]:
    if os.name == "nt":
        powershell = next((name for name in ("pwsh", "powershell") if shutil.which(name)), None)
        if powershell is None:
            raise SystemExit("PowerShell is required for TV changes on Windows")
        script = TOOLS / ("disable.ps1" if action == "apply" else "restore.ps1")
        return [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), str(list_path)]
    return ["bash", str(TOOLS / ("disable.sh" if action == "apply" else "restore.sh")), str(list_path)]


def change(action: str, list_path: Path) -> int:
    try:
        names = recovery.read_list(list_path)
    except SystemExit:
        raise
    if action == "apply" and not names:
        raise SystemExit("the plan has no approved packages")
    result = subprocess.run(script_command(action, list_path), cwd=ROOT, env=os.environ.copy())
    return result.returncode


def install_launcher(input_key_service: bool, home_key_service: bool, restore_key_services: bool,
                     stock_launcher: str | None) -> int:
    host = os.environ.get("TV_HOST")
    if not host:
        raise SystemExit("set TV_HOST to the TV IP address")
    env = os.environ.copy()
    if os.name == "nt":
        powershell = next((name for name in ("pwsh", "powershell") if shutil.which(name)), None)
        if powershell is None:
            raise SystemExit("PowerShell is required for TV changes on Windows")
        command = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                   str(ROOT / "launcher" / "build-and-install.ps1"), "-TvHost", host]
        if stock_launcher:
            command += ["-StockLauncher", stock_launcher]
        if input_key_service:
            command.append("-InputKeyService")
        if home_key_service:
            command.append("-HomeKeyService")
        if restore_key_services:
            command.append("-RestoreKeyServices")
    else:
        command = ["bash", str(ROOT / "launcher" / "build-and-install.sh")]
        if stock_launcher:
            env["STOCK_LAUNCHER"] = stock_launcher
        if input_key_service:
            env["INPUT_KEY_SERVICE"] = "1"
        if home_key_service:
            env["HOME_KEY_SERVICE"] = "1"
        if restore_key_services:
            env["RESTORE_KEY_SERVICES"] = "1"
    return subprocess.run(command, cwd=ROOT, env=env).returncode


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    scan_p = sub.add_parser("scan", help="read a TV without changing it")
    scan_p.add_argument("--out", type=Path, required=True)
    plan = sub.add_parser("plan", help="make a review-only or explicitly approved disable plan")
    plan.add_argument("--scan", type=Path, required=True)
    plan.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    plan.add_argument("--out", type=Path, required=True)
    plan.add_argument("--keep", action="append", default=[], help="package to preserve; repeat this option")
    plan.add_argument("--approve", action="append", default=[], help="package to approve; repeat this option")
    plan.add_argument("--acknowledge-mismatch", action="store_true")
    config = sub.add_parser("config", help="make a local theme config for dock and remote keys")
    config.add_argument("--out", type=Path, required=True)
    config.add_argument("--dock", default="", help="comma-separated package names")
    config.add_argument("--app-key", action="append", default=[])
    config.add_argument("--columns", type=int, default=6)
    for name, help_text in (("apply", "apply an approved plan"), ("restore", "restore a previous plan")):
        action = sub.add_parser(name, help=help_text)
        action.add_argument("plan", type=Path)
    install = sub.add_parser("install", help="build and install the existing launcher with optional key helpers")
    install.add_argument("--input-key-service", action="store_true")
    install.add_argument("--home-key-service", action="store_true")
    install.add_argument("--restore-key-services", action="store_true")
    install.add_argument("--stock-launcher", help="explicit stock launcher package, or 'none'")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "scan":
        return scan(args.out)
    if args.command == "plan":
        return write_plan(args.scan, args.out, args.reference, args.keep, args.approve,
                          args.acknowledge_mismatch)
    if args.command == "config":
        return write_config(args.out, [x for x in args.dock.split(",") if x], args.app_key, args.columns)
    if args.command == "install":
        return install_launcher(args.input_key_service, args.home_key_service, args.restore_key_services,
                                args.stock_launcher)
    return change(args.command, args.plan)


if __name__ == "__main__":
    sys.exit(main())
