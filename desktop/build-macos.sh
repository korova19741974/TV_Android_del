#!/usr/bin/env bash
set -euo pipefail

# Build a self-contained macOS application and DMG. The launcher APK must already be built; the
# GitHub workflow does that once, then embeds it so a user does not need JDK or Android SDK.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
VERSION="${VERSION:-dev}"
APK="${APK:-$ROOT/launcher/app/build/outputs/apk/release/app-release.apk}"
BUILD_ROOT="$ROOT/desktop/build-macos"
DIST_ROOT="$ROOT/desktop/dist-macos"
STAGE="$BUILD_ROOT/resources"
VENV="$BUILD_ROOT/venv"

fail() { echo "Ошибка: $*" >&2; exit 1; }

[ -f "$APK" ] || fail "не найден APK лаунчера: $APK"
command -v "$PYTHON" >/dev/null 2>&1 || fail "не найден Python 3"
command -v hdiutil >/dev/null 2>&1 || fail "сборка DMG выполняется только на macOS"

rm -rf "$BUILD_ROOT" "$DIST_ROOT"
mkdir -p "$STAGE/tools" "$STAGE/launcher/app" "$STAGE/examples" "$STAGE/prebuilt" "$DIST_ROOT"

"$PYTHON" -m venv --copies "$VENV"
"$VENV/bin/python" -m pip install --disable-pip-version-check --upgrade pip pyinstaller
"$VENV/bin/python" -m pip install --disable-pip-version-check -r "$ROOT/tools/requirements.txt"

# Copy only files needed by the GUI and its safe install/theme paths. In particular, never copy a
# developer's local tools/adbkey into a distributed application.
for file in "$ROOT"/tools/*.py "$ROOT"/tools/theme.sh "$ROOT"/tools/requirements.txt; do
  [ -f "$file" ] && cp "$file" "$STAGE/tools/"
done
cp "$ROOT/launcher/build-and-install.sh" "$STAGE/launcher/"
cp "$ROOT/launcher/app/build.gradle" "$STAGE/launcher/app/"
cp -R "$ROOT/examples/." "$STAGE/examples/"
cp "$APK" "$STAGE/prebuilt/app-release.apk"
chmod +x "$STAGE/tools/theme.sh" "$STAGE/launcher/build-and-install.sh"

"$VENV/bin/python" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name CleanYourTV \
  --osx-bundle-identifier com.gathin.cleanyourtv \
  --distpath "$DIST_ROOT" \
  --workpath "$BUILD_ROOT/pyinstaller" \
  --specpath "$BUILD_ROOT/pyinstaller" \
  --paths "$ROOT" \
  --hidden-import tools.unified \
  --hidden-import tools.tv \
  --hidden-import tools.b64push \
  --hidden-import tools.theme_restart \
  --hidden-import recovery \
  --hidden-import catalog \
  --add-data "$STAGE/tools:tools" \
  --add-data "$STAGE/launcher:launcher" \
  --add-data "$STAGE/examples:examples" \
  --add-data "$STAGE/prebuilt:prebuilt" \
  "$ROOT/desktop/CleanYourTV.py"

APP="$DIST_ROOT/CleanYourTV.app"
[ -d "$APP" ] || fail "PyInstaller не создал CleanYourTV.app"
hdiutil create -volname "CleanYourTV $VERSION" -srcfolder "$APP" \
  -ov -format UDZO "$DIST_ROOT/CleanYourTV-macOS-$(uname -m)-$VERSION.dmg" >/dev/null

echo "Готово: $DIST_ROOT/CleanYourTV-macOS-$(uname -m)-$VERSION.dmg"
