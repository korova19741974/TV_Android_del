# Unified TV setup

`tools/unified.py` is the single entry point for a cautious cleanup. It combines the useful parts of the
project's inventory, reversible debloat, launcher configuration and remote-key mapping without introducing a
second ADB client or an uninstall path.

## Safe workflow

```text
TV_HOST=<tv ip> python tools/unified.py scan --out work/mztu1-scan
python tools/unified.py plan --scan work/mztu1-scan --out work/mztu1-plan.txt
```

The first command only reads the TV. The second command creates a review-only plan: candidates are comments,
so the file cannot change the TV by accident. Add only the packages you have reviewed:

```text
python tools/unified.py plan --scan work/mztu1-scan \
  --out work/mztu1-plan.txt \
  --keep com.google.android.youtube.tv \
  --approve com.example.package \
  --acknowledge-mismatch
```

`--acknowledge-mismatch` is required when the reference list is not an exact profile for the scanned TV. The
closest Xiaomi Android 14 list is `examples/xiaomi-tv-a-pro-2026/debloat.txt`, which is a reference for MZTU0,
not proof that it is safe for MZTU1. Core Android packages are rejected, and setupwraith is excluded when the
scan shows that it owns the saved Wi-Fi network.

Apply and undo use the existing safety-checked scripts:

```text
TV_HOST=<tv ip> python tools/unified.py apply work/mztu1-plan.txt
TV_HOST=<tv ip> python tools/unified.py restore work/mztu1-plan.txt
```

## Dock and remote keys

Make a local theme config without installing anything:

```text
python tools/unified.py config --out work/mztu1-theme \
  --columns 6 \
  --dock com.google.android.youtube.tv,org.xbmc.kodi,com.netflix.ninja \
  --app-key 190:com.google.android.youtube.tv
```

Review `work/mztu1-theme/config.json`, then push it with the existing `tools/theme.sh`. Accessibility key
helpers still require the corresponding launcher install flag (`-InputKeyService` or `-HomeKeyService`) and a
real press of each physical remote button; an injected ADB key is not proof that the real button works.

The same entry point can run the existing launcher build/handover guard:

```text
TV_HOST=<tv ip> python tools/unified.py install --input-key-service --home-key-service
```

It does not silently enable either accessibility helper. Pass only the helper you have calibrated with the real
remote; `--restore-key-services` is optional and grants the launcher secure-settings access so the helpers can be
restored after a force-stop.
