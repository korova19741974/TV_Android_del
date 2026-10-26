#!/usr/bin/env python3
"""Small Windows window for the common CleanYourTV actions."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        if (parent / "launcher").is_dir() and (parent / "tools").is_dir():
            return parent
    return here.parent.parent


ROOT = application_root()
sys.path.insert(0, str(ROOT))
from tools import unified  # noqa: E402

APP_LABELS = {
    "com.google.android.youtube.tv": "YouTube",
    "com.netflix.ninja": "Netflix",
    "org.videolan.vlc": "VLC",
    "org.xbmc.kodi": "Kodi",
    "com.plexapp.android": "Plex",
    "com.google.android.apps.tv.launcherx": "Google TV",
    "com.google.android.tungsten.setupwraith": "Настройка Android TV",
    "com.android.tv.settings": "Настройки телевизора",
}


def app_label(package: str) -> str:
    return f"{APP_LABELS.get(package, package)}  —  {package}"


class CleanYourTVApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CleanYourTV — помощник телевизора")
        self.root.geometry("920x750")
        self.root.minsize(820, 680)
        self.root.configure(bg="#F8FAFC")
        self.apps: list[str] = []
        self.host = ""
        self.out = ROOT / "work" / "desktop-tv"
        self.status = tk.StringVar(value="Введите адрес телевизора и нажмите «Подключить».")
        self.host_var = tk.StringVar()
        self.background_var = tk.StringVar(value="#101820")
        self.sleep_key_info_var = tk.StringVar(value="Кнопка не выбрана")
        self.sleep_key_binding = ""
        self.wallpaper_var = tk.StringVar(value="Обои не выбраны")
        self.wallpaper_path: Path | None = None
        self.clear_wallpaper = False
        self.show_time_var = tk.BooleanVar(value=True)
        self.show_date_var = tk.BooleanVar(value=True)
        self.weather_city_var = tk.StringVar(value="Санкт-Петербург, Россия")
        self.auto_sort_dock_var = tk.BooleanVar(value=True)
        self.busy = False
        self._build()

    def _build(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground="#1E293B")
        style.configure("Body.TLabel", font=("Segoe UI", 13), foreground="#475569")
        style.configure("Section.TLabel", font=("Segoe UI", 15, "bold"), foreground="#1E293B")
        style.configure("Big.TButton", font=("Segoe UI", 13, "bold"), padding=(18, 12))
        style.configure("Small.TButton", font=("Segoe UI", 11), padding=(10, 8))

        outer = ttk.Frame(self.root, padding=28)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Настройка телевизора", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Подключите ТВ, выберите приложения и сохраните настройки.",
                  style="Body.TLabel").pack(anchor="w", pady=(4, 20))

        connection = ttk.LabelFrame(outer, text="1. Подключение", padding=16)
        connection.pack(fill="x", pady=(0, 14))
        ttk.Label(connection, text="IP-адрес телевизора", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(connection, textvariable=self.host_var, width=24, font=("Segoe UI", 13)).grid(
            row=0, column=1, padx=12, sticky="ew")
        ttk.Button(connection, text="Подключить и проверить", style="Big.TButton",
                   command=self.connect).grid(row=0, column=2, sticky="e")
        connection.columnconfigure(1, weight=1)

        apps_frame = ttk.LabelFrame(outer, text="2. Приложения на главном экране", padding=16)
        apps_frame.pack(fill="both", expand=True, pady=(0, 14))
        ttk.Label(apps_frame, text="Выберите не более шести приложений. После установки APK нажмите «Обновить список».",
                  style="Body.TLabel").pack(anchor="w", pady=(0, 8))
        list_row = ttk.Frame(apps_frame)
        list_row.pack(fill="both", expand=True)
        self.app_list = tk.Listbox(list_row, selectmode=tk.MULTIPLE, exportselection=False,
                                   font=("Segoe UI", 14), activestyle="none", selectbackground="#2563EB",
                                   selectforeground="white", relief="solid", borderwidth=1)
        self.app_list.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(list_row, orient="vertical", command=self.app_list.yview)
        scroll.pack(side="right", fill="y")
        self.app_list.configure(yscrollcommand=scroll.set)
        buttons = ttk.Frame(apps_frame)
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Выбрать APK на компьютере", style="Small.TButton",
                   command=self.install_apk).pack(side="left")
        ttk.Button(buttons, text="Обновить список", style="Small.TButton",
                   command=self.refresh).pack(side="left", padx=8)

        settings = ttk.LabelFrame(outer, text="3. Простые настройки", padding=16)
        settings.pack(fill="x", pady=(0, 14))
        ttk.Label(settings, text="Цвет фона", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.background_var, width=12, font=("Segoe UI", 12)).grid(
            row=0, column=1, padx=10, sticky="w")
        ttk.Button(settings, text="Выбрать цвет", style="Small.TButton", command=self.choose_color).grid(
            row=0, column=2, sticky="w")
        ttk.Button(settings, text="Выбрать обои", style="Small.TButton", command=self.choose_wallpaper).grid(
            row=0, column=3, padx=(22, 8), sticky="w")
        ttk.Button(settings, text="Убрать обои", style="Small.TButton", command=self.remove_wallpaper).grid(
            row=0, column=4, sticky="w")
        ttk.Label(settings, textvariable=self.wallpaper_var, style="Body.TLabel").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(9, 0))
        ttk.Checkbutton(settings, text="Показывать время", variable=self.show_time_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Checkbutton(settings, text="Показывать дату", variable=self.show_date_var).grid(
            row=2, column=2, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Label(settings, text="Город для погоды", style="Body.TLabel").grid(
            row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(settings, textvariable=self.weather_city_var, width=22, font=("Segoe UI", 12)).grid(
            row=3, column=1, columnspan=2, padx=10, sticky="w", pady=(10, 0))
        ttk.Label(settings, text="оставьте пустым, чтобы скрыть погоду", style="Body.TLabel").grid(
            row=3, column=3, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Checkbutton(settings, text="Автоматически сортировать док по последним запускам",
                        variable=self.auto_sort_dock_var).grid(
            row=4, column=0, columnspan=5, sticky="w", pady=(10, 0))
        ttk.Label(settings, text="Кнопка сна", style="Body.TLabel").grid(
            row=5, column=0, padx=(0, 10), sticky="w", pady=(10, 0))
        ttk.Button(settings, text="Настройка кнопки сна", style="Small.TButton",
                   command=self.configure_sleep_button).grid(
            row=5, column=1, sticky="w", pady=(10, 0))
        ttk.Button(settings, text="Сбросить", style="Small.TButton",
                   command=self.clear_sleep_button).grid(
            row=5, column=2, padx=(8, 0), sticky="w", pady=(10, 0))
        ttk.Label(settings, textvariable=self.sleep_key_info_var, style="Body.TLabel").grid(
            row=5, column=3, columnspan=2, padx=(16, 0), sticky="w", pady=(10, 0))

        actions = ttk.Frame(outer)
        actions.pack(fill="x")
        ttk.Button(actions, text="Сохранить настройки на ТВ", style="Big.TButton",
                   command=self.apply_theme).pack(side="left")
        ttk.Button(actions, text="Установить лаунчер", style="Big.TButton",
                   command=self.install_launcher).pack(side="left", padx=10)
        ttk.Label(outer, textvariable=self.status, style="Body.TLabel", wraplength=860).pack(
            anchor="w", pady=(14, 0))

    def set_busy(self, text: str) -> None:
        self.status.set(text)
        self.busy = True
        self.set_controls_enabled(False)
        self.root.update_idletasks()

    def set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"

        def visit(widget: tk.Misc) -> None:
            for child in widget.winfo_children():
                if isinstance(child, (tk.Entry, tk.Listbox, ttk.Button, ttk.Checkbutton, ttk.Entry)):
                    child.configure(state=state)
                visit(child)

        visit(self.root)

    def finish_async(self) -> None:
        self.busy = False
        self.set_controls_enabled(True)

    def run_async(self, label: str, work, done) -> None:
        if self.busy:
            return
        self.set_busy(label)

        def worker() -> None:
            try:
                result = work()
            except (Exception, SystemExit) as exc:  # the dialog is the user-facing error boundary
                error_text = str(exc)
                self.root.after(0, lambda: (self.finish_async(), self.status.set(
                    "Действие не выполнено. Можно попробовать ещё раз."),
                    messagebox.showerror("Не удалось выполнить действие", error_text)))
            else:
                self.root.after(0, lambda: (self.finish_async(), done(result)))

        threading.Thread(target=worker, daemon=True).start()

    def connect(self) -> None:
        host = self.host_var.get().strip()
        if not host:
            messagebox.showwarning("Нужен адрес", "Введите IP-адрес телевизора, например 192.168.1.50.")
            return
        self.host = host
        os.environ["TV_HOST"] = host
        self.run_async("Читаю данные телевизора… Подтвердите доступ на экране ТВ, если появится запрос.",
                       lambda: (unified.scan(self.out), unified.load_scan(self.out))[1], self.show_scan)

    def refresh(self) -> None:
        if not self.host:
            messagebox.showwarning("Нет подключения", "Сначала подключите телевизор.")
            return
        self.connect()

    def show_scan(self, data: dict) -> None:
        self.apps = [app for app in data.get("apps", []) if isinstance(app, str)]
        self.app_list.delete(0, tk.END)
        for app in self.apps:
            self.app_list.insert(tk.END, app_label(app))
        self.status.set(f"Телевизор подключён. Найдено приложений: {len(self.apps)}. Выберите нужные.")

    def install_apk(self) -> None:
        if not self.host:
            messagebox.showwarning("Нет подключения", "Сначала подключите телевизор.")
            return
        apk = filedialog.askopenfilename(title="Выберите APK-файл", filetypes=[("Android APK", "*.apk")])
        if not apk:
            return
        self.run_async("Передаю APK на телевизор и устанавливаю…",
                       lambda: (unified.install_apk(Path(apk)), unified.scan(self.out), unified.load_scan(self.out))[2],
                       lambda data: (self.show_scan(data), messagebox.showinfo(
                           "Готово", "Приложение установлено. Выберите его в списке и сохраните настройки на ТВ.")))

    def choose_color(self) -> None:
        chosen = colorchooser.askcolor(title="Цвет фона", initialcolor=self.background_var.get())[1]
        if chosen:
            self.background_var.set(chosen.upper())

    def choose_wallpaper(self) -> None:
        selected = filedialog.askopenfilename(
            title="Выберите изображение для обоев",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.webp")],
        )
        if selected:
            self.wallpaper_path = Path(selected)
            self.clear_wallpaper = False
            self.wallpaper_var.set(f"Обои: {self.wallpaper_path.name}")

    def remove_wallpaper(self) -> None:
        self.wallpaper_path = None
        self.clear_wallpaper = True
        self.wallpaper_var.set("Обои будут убраны")

    def configure_sleep_button(self) -> None:
        if not self.host:
            messagebox.showwarning("Нет подключения", "Сначала подключите телевизор.")
            return
        self.run_async(
            "Нажмите и удерживайте нужную кнопку на пульте, например Netflix…",
            lambda: unified.learn_remote_key(),
            self.show_sleep_key,
        )

    def show_sleep_key(self, key: dict[str, int | str]) -> None:
        keycode = int(key["keycode"])
        scancode = int(key["scancode"])
        if keycode > 0:
            self.sleep_key_binding = str(keycode)
        elif scancode > 0:
            self.sleep_key_binding = f"scan:{scancode}"
        else:
            messagebox.showwarning("Кнопка не распознана", "Телевизор не вернул пригодный код этой кнопки.")
            return
        name = str(key["name"]).removeprefix("KEYCODE_")
        self.sleep_key_info_var.set(f"Выбрана: {name} (код найден автоматически)")
        self.status.set("Кнопка запомнена. Нажмите «Сохранить настройки на ТВ», затем установите лаунчер.")

    def clear_sleep_button(self) -> None:
        self.sleep_key_binding = ""
        self.sleep_key_info_var.set("Кнопка не выбрана")
        self.status.set("Настройка кнопки сна отменена.")

    def selected_packages(self) -> list[str]:
        chosen = [self.apps[index] for index in self.app_list.curselection()]
        if not chosen:
            raise ValueError("Выберите хотя бы одно приложение.")
        if len(chosen) > 6:
            raise ValueError("Можно выбрать не более шести приложений.")
        return chosen

    def apply_theme(self) -> None:
        if not self.host:
            messagebox.showwarning("Нет подключения", "Сначала подключите телевизор.")
            return
        try:
            packages = self.selected_packages()
            app_keys = [f"hold:{self.sleep_key_binding}:sleep"] if self.sleep_key_binding else []
            self.out.mkdir(parents=True, exist_ok=True)
            wallpaper_target = self.out / "wallpaper.jpg"
            if self.wallpaper_path:
                shutil.copyfile(self.wallpaper_path, wallpaper_target)
            elif self.clear_wallpaper and wallpaper_target.exists():
                wallpaper_target.unlink()
            unified.write_config(
                self.out,
                packages,
                app_keys,
                6,
                self.background_var.get().strip(),
                self.show_time_var.get(),
                self.show_date_var.get(),
                self.weather_city_var.get(),
                self.auto_sort_dock_var.get(),
            )
        except (SystemExit, ValueError) as exc:
            messagebox.showwarning("Проверьте настройки", str(exc))
            return
        self.run_async("Отправляю настройки на телевизор…", self.push_theme,
                       lambda _: self.status.set("Настройки сохранены на ТВ."))

    def push_theme(self) -> str:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            raise RuntimeError("На компьютере не найден PowerShell.")
        script = ROOT / "tools" / "theme.ps1"
        result = subprocess.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                 str(script), str(self.out), "-TvHost", self.host],
                                cwd=ROOT, capture_output=True, text=True,
                                errors="replace",
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "не удалось отправить настройки")
        return result.stdout

    def install_launcher(self) -> None:
        if not self.host:
            messagebox.showwarning("Нет подключения", "Сначала подключите телевизор.")
            return
        if not messagebox.askyesno("Установка лаунчера", "Установить CleanYourTV как главный экран телевизора?"):
            return
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            messagebox.showerror("Ошибка", "На компьютере не найден PowerShell.")
            return
        script = ROOT / "launcher" / "build-and-install.ps1"
        def build() -> str:
            result = subprocess.run(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                 "-TvHost", self.host, "-InputKeyService", "-HomeKeyService"],
                cwd=ROOT, capture_output=True, text=True,
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "сборка лаунчера не удалась")
            return result.stdout

        self.run_async("Собираю и устанавливаю лаунчер…", build,
                       lambda _: self.status.set("Лаунчер установлен. Проверьте кнопки пульта."))


def main() -> None:
    root = tk.Tk()
    CleanYourTVApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
