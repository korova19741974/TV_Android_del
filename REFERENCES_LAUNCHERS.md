# Аудит Android TV launchers и смежных источников для CleanYourTV

Дата среза: 2026-10-26. Источники проверены как первичные: содержимое README, исходный код и файлы лицензий самих репозиториев; для gist — текст самого gist. Внешние статьи, обзоры, магазины приложений и маркетинговые страницы не использовались как основание выводов.

Важно различать типы источников:

- `tellyscope` — companion-приложение на телефоне для управления Android TV и деблоата, а не домашний launcher;
- `Awesome-Android-TV-FOSS-Apps` и gist — каталоги/списки, не реализации интерфейса;
- `tv-launcher` — экспериментальный проект с частью функций в статусе planned;
- остальные записи — launcher-приложения или дистрибутивный репозиторий APK.

## Краткий вывод для CleanYourTV

Самая практичная комбинация для CleanYourTV — безопасность и обратимость Tellyscope, компактная информационная архитектура Plume, локальность Material TV Launcher и дисциплина D-pad-навигации из LTvLauncher/Arc Launcher. В первой версии не стоит превращать CleanYourTV в универсальный launcher с обоями, погодой, уведомлениями и медиаплеером: это размывает задачу очистки ТВ.

Приоритетные идеи, которые можно реализовать независимо, без копирования кода или ассетов:

1. **Предварительный просмотр изменений:** перед операцией показать точный список пакетов, причину рекомендации, риск и ожидаемый результат; защищённые системные компоненты исключать из выбора.
2. **История per-TV + Undo/Restore all:** хранить изменения отдельно для каждого телевизора, поддерживать отмену каждой обратимой операции и общий возврат состояния.
3. **Режим “сначала безопасное”:** отдельно показывать пользовательские приложения, встроенные приложения и защищённую систему; uninstall разрешать только для явно пользовательских пакетов.
4. **Управление с пульта:** row-by-row focus traversal, заметный focus без толстых рамок, удержание OK для контекстных действий, сохранение фокуса после перемещения.
5. **Локальность по умолчанию:** не добавлять сеть, аналитику и аккаунт, если функция не требует этого; показывать разрешения и последствия до их включения.
6. **Тестируемая модель устройств:** обнаружение/подключение, состояние offline, last-seen, понятные состояния pairing и восстановления связи.
7. **Осмысленная визуальная система:** тёмная OLED-дружественная база, спокойные карточки и один акцентный цвет состояния; адаптивный цвет можно добавить как опциональный слой, но не делать его обязательным.

## Сравнительная матрица

| Источник | Основная функция | Навигация и взаимодействие | Визуальный язык | Лицензия / практический вывод |
|---|---|---|---|---|
| [Tellyscope](https://github.com/man15h/tellyscope) | Управление ТВ с телефона: ADB, деблоат, APK, файлы, remote, tweaks | Экран конкретного ТВ, вкладки Apps/Files/Tweaks, поиск и закреплённые controls; D-pad с повтором при удержании; dock приложений с long-press/drag | Material 3 Expressive, карточки, статусы online/offline, цветовые состояния, компактный top bar | GPL-3.0; при заимствовании кода нужно соблюдать copyleft и NOTICE. Идеи workflow можно реализовать самостоятельно |
| [Monet Launcher](https://github.com/Klevico/Monet-Launcher) | Launcher с динамическими цветами, рядами, папками, профилями, PIN, screensaver и backup | README заявляет show/hide/reorder рядов и favorites dock, но исходники в репозитории отсутствуют | Цветовая тема от wallpaper, кастомные wallpapers, blur/brightness | Лицензия не указана, LICENSE нет; README прямо говорит, что это только APK-дистрибутив. Код и ассеты не использовать |
| [Awesome Android TV FOSS Apps](https://github.com/Generator/Awesome-Android-TV-FOSS-Apps) | Каталог FOSS-приложений и критериев пригодности для ТВ | Не реализация; полезны легенда remote support/TV icon/root/compatibility и раздел Launcher | Собственного UI нет | CC BY-NC-SA 4.0 для списка; не лицензия кода перечисленных проектов и не подходящая база для кода CleanYourTV |
| [TV Launcher](https://github.com/nielsvanvelzen/tv-launcher) | Ранний launcher-проект: toolbar, favorites, channels, all apps, TV inputs | Код разделяет Home/Apps, toolbar и источники данных App/Channel/Input; часть функций README помечает как planned | Экспериментальный минимальный Leanback-подход; wallpaper и search явно отнесены к unplanned/platform limits | GPL-3.0; использовать как архитектурный ориентир, не как готовый feature baseline |
| [Android TV: Debloat + Custom Launcher](https://github.com/product-noob/android-tv-launcher) | Apple TV-подобный launcher с apps/recent/HDMI/trending + отдельные debloat scripts | Rows, long-press tile для move/favorites/App info; header actions; HDMI tiles | Frosted glass, full-bleed rows, lift + color glow, Inter, pure-black OLED care | MIT; код можно переиспользовать при сохранении MIT notice, но TMDB/Inter/ассеты имеют отдельные условия |
| [Alternative launchers gist](https://gist.github.com/denilsonsa/80cbb3a14b3bf63de75e6bf81c89ee05) | Невалидируемый по коду каталог альтернативных launchers и wish-list | Не реализация; wish-list: folders/tags, sorting, sideloaded apps, >3 tiles, App Info, clock/date, no ads | Собственного UI нет | Отдельной лицензии в gist не обнаружено; использовать только как авторский список требований/контекст, не как кодовую базу |
| [Plume Launcher](https://github.com/aradhyas8/Plume_Launcher) | Минималистичный launcher: apps + Continue Watching, HDMI sources, remote remap, wallpapers/screensaver | Single apps row, All apps, top-bar Sources; hold OK для reorder/hide/pin; press/hold для переназначения клавиш; PIN lock layout | Минимализм, light/dark/auto, собственные wallpaper и мягкий fade для читаемости; очень маленький APK | GPL-3.0; производные распространяемые версии должны оставаться GPL-3.0 с исходниками |
| [Arc Launcher](https://github.com/meddouribadis/arclauncher) | Fork LTvLauncher: grid, Watch Next, categories, wallpapers, OLED, updater, sideloaded apps | Настраиваемые rows/columns; Left/Right для перестановки категорий; high-visibility double-border focus; auto-hide status bar | Accent presets, blur, video/slideshow/dynamic wallpapers, OLED theme | GPL-3.0; учитывать fork lineage и copyleft |
| [LTvLauncher](https://github.com/leanbitlab-org/LtvLauncher) | Полнофункциональный launcher: Watch Next, категории, weather/status, inputs, notifications, backups, OLED | Native D-pad, row/grid categories, reorder/rename/hide, settings panels, Home Button Fix | 4 card themes, accent colors, custom banners, dynamic day/night/OLED backgrounds, focus outline | GPL-3.0; код/производные — с GPL-3.0 и исходниками |
| [Material TV Launcher](https://github.com/0xRampey/material-tv-launcher) | Локальный launcher по фактическому использованию, HDMI-CEC devices, Now Playing, screensaver | Home/Apps/Settings, горизонтальный dock из шести наиболее используемых приложений, focus enlarges tile; Home Button accessibility service | Material 3 Expressive, palette от banner focused app, morphing shapes, spring motion, equalizer/progress | Apache-2.0; bundled material-color-utilities Apache-2.0, Google Sans Flex — SIL OFL 1.1 |

## Детальный разбор

### 1. Tellyscope — наиболее близкий источник по задаче очистки

Это не launcher, а телефонный control plane для Android TV: подключение по classic network debugging и Android 11+ wireless debugging, список устройств, состояние ТВ, управление приложениями, установка APK, передача файлов, remote и системные tweaks. README описывает три группы Apps — Running, Installed и Built-in — и отдельную защищённую секцию System. Для нового launcher Tellyscope умеет сначала назначить новый Home, проверить, что Home действительно открывается, и только затем отключить старый launcher.

Главная ценность для CleanYourTV — safety model, а не внешний вид:

- protected list без override для пакетов, необходимых для boot, updates, Wi-Fi, Home и input;
- disabling встроенных приложений вместо удаления;
- пользовательский uninstall только после явного подтверждения и с предупреждением, что операция необратима;
- запись каждого изменения в History, Undo и Restore everything;
- просмотр точного списка изменений до выполнения;
- per-TV state, reconnect и offline/last-seen состояние;
- собственный fork списков debloat, если пользователь не хочет доверять встроенным.

Код подтверждает модель: [DeviceScreen.kt](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/app/src/main/java/app/tellyscope/ui/DeviceScreen.kt) содержит UI истории, protected/home-state и подтверждений; [AppsTabs.kt](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/app/src/main/java/app/tellyscope/ui/AppsTabs.kt) разделяет Running/Installed/Built-in и сворачиваемую System-секцию; [RemoteScreen.kt](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/app/src/main/java/app/tellyscope/ui/RemoteScreen.kt) реализует D-pad, repeat-on-hold, haptics, dock и drag reorder. Визуальную систему задаёт [Theme.kt](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/app/src/main/java/app/tellyscope/ui/theme/Theme.kt).

Для CleanYourTV применить: protected package model, staged plan, history/undo, health status, last-seen, safe launcher switch, понятные copy-тексты. Не переносить буквально код ADB, UI или иконки. Лицензия проекта — [GPL-3.0](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/LICENSE); дополнительные компоненты и их лицензии перечислены в [NOTICE](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/NOTICE).

### 2. Monet Launcher — сильная матрица функций, но закрытый источник

README перечисляет динамические цвета от wallpaper, пользовательские/встроенные/aerial/Reddit wallpapers, auto-rotation, blur и brightness; виджеты clock/date/weather/now playing/network/Bluetooth; reorderable home rows — Continue Watching, Recommendations, Live TV, favorites, all apps, HDMI; custom artwork, icon shapes/packs; folders; hide/rename/uninstall; multiple profiles; per-app PIN; screensaver; autostart; themes; adjustable app size/grid; backup/restore.

Навигационная модель описана только на уровне возможностей: favorites dock, show/hide/reorder rows, folders и app management. Исходников в репозитории нет, поэтому нельзя проверить конкретную focus traversal model, жесты, permission handling или детали UI. README сообщает, что репозиторий предназначен только для распространения APK и source code не входит в него.

Для CleanYourTV применимы только продуктовые идеи: progressive setup, управляемая плотность rows, folders/categories, PIN на опасные настройки, backup/restore и разделение launcher-функций на включаемые блоки. Не использовать код, закрытые ассеты или скриншот как основу дизайна. [README](https://github.com/Klevico/Monet-Launcher/blob/a6a213c5e6a80067ab3d5c633b2eb54e4cc20b00/README.md); LICENSE-файла в репозитории нет.

### 3. Awesome Android TV FOSS Apps — источник требований и discovery, не UI-референс

Это curated list, где есть отдельная категория Launcher и легенда практических ограничений: partial remote support, отсутствие TV launcher icon, root, несовместимость с некоторыми устройствами, non-free components, paid features и остановка разработки. В авторском wish-list для хорошего launcher перечислены folders/tags, сортировка, native TV + sideloaded apps, больше трёх элементов в row, App Info/Force Close, time/date, отсутствие рекламы/интрузивных permissions, open source и F-Droid.

Для CleanYourTV полезно превратить эту wish-list в acceptance criteria: remote-complete navigation, sideloaded visibility, понятное управление пакетами, отсутствие рекламы и минимальные permissions. Визуального или навигационного кода здесь нет. Репозиторий лицензирован [CC BY-NC-SA 4.0](https://github.com/Generator/Awesome-Android-TV-FOSS-Apps/blob/9f0c751ff58b609cee1c482d4634c53c250f266/LICENSE): это лицензия самого списка, а не лицензии всех перечисленных приложений.

### 4. TV Launcher — полезная ранняя модель домена

README явно отделяет planned features от unplanned. В planned: configurable toolbar с clock/settings/TV input sources, favorites с hide/reorder, channels и all-apps grid с возможностью показывать mobile apps. В unplanned — wallpapers и search; README связывает невозможность wallpaper с отсутствием соответствующей реализации WallpaperManager на Android TV.

Кодовая структура хорошо раскладывает домен: [LauncherScreen.kt](https://github.com/nielsvanvelzen/tv-launcher/blob/a0149305678b243e18cd573c0268a99683ee9558/app/src/main/kotlin/nl/ndat/tvlauncher/ui/screen/launcher/LauncherScreen.kt), Home/Apps tabs, toolbar и отдельные [AppRepository](https://github.com/nielsvanvelzen/tv-launcher/blob/a0149305678b243e18cd573c0268a99683ee9558/app/src/main/kotlin/nl/ndat/tvlauncher/data/repository/AppRepository.kt), [ChannelRepository](https://github.com/nielsvanvelzen/tv-launcher/blob/a0149305678b243e18cd573c0268a99683ee9558/app/src/main/kotlin/nl/ndat/tvlauncher/data/repository/ChannelRepository.kt) и [InputRepository](https://github.com/nielsvanvelzen/tv-launcher/blob/a0149305678b243e18cd573c0268a99683ee9558/app/src/main/kotlin/nl/ndat/tvlauncher/data/repository/InputRepository.kt).

Для CleanYourTV применимы узкие data boundaries: device/app/input/channel как разные источники, а не один монолитный список. При этом не следует принимать planned-функции за доказанную готовность. Лицензия — [GPL-3.0](https://github.com/nielsvanvelzen/tv-launcher/blob/a0149305678b243e18cd573c0268a99683ee9558/LICENSE).

### 5. Android TV: Debloat + Custom Launcher — Apple TV-подобная визуальная модель

README описывает связку из двух частей: reversible debloat scripts и launcher на Kotlin/Jetpack Compose for TV. Launcher даёт optional TMDB Trending this week с backdrop/logo/rating/summary и deep link к установленному streaming app; favorites row, all-apps row, Recent без favorites; HDMI inputs как tiles с именем CEC-устройства; header с clock/greeting/date/weather и Picture/Sound/Wi-Fi/Settings; OLED care с pure black, pixel drift и dimming.

Навигационно важны long-press actions на tile — Move, Add/Remove favorites, App info — и запоминаемый порядок favorites. Визуально это intentionally cinematic: frosted-glass controls, rows, уходящие за край, focus через lift + цветовой glow вместо толстой рамки. Кодовые точки: [HomeScreen.kt](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/launcher/app/src/main/java/me/prince/launcher/HomeScreen.kt), [Glass.kt](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/launcher/app/src/main/java/me/prince/launcher/Glass.kt), [Apps.kt](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/launcher/app/src/main/java/me/prince/launcher/Apps.kt), [Trending.kt](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/launcher/app/src/main/java/me/prince/launcher/Trending.kt), [Inputs.kt](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/launcher/app/src/main/java/me/prince/launcher/Inputs.kt).

Для CleanYourTV можно применить: long-press context menu, focus lift/glow, OLED care и named HDMI devices. Trending/TMDB в ядро очистки не нужен. Лицензия основного репозитория — [MIT](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/LICENSE); bundled Inter имеет отдельный файл [Inter-OFL.txt](https://github.com/product-noob/android-tv-launcher/blob/e5f5ed2c33abb0cc61393b5451c45d6c85f23686/launcher/third_party/Inter-OFL.txt), поэтому ассеты нельзя считать автоматически MIT.

### 6. Gist с альтернативными launchers — исторический discovery list

Автор сам описывает gist как неполный список и не endorsement. Он смешивает коммерческие/бесплатные, ad-supported и open-source launchers, а также отмечает риски intrusive permissions. Внутри есть ссылки на Monet, FLauncher, LTvLauncher, Arc и `nielsvanvelzen/tv-launcher`; отдельный wish-list повторяет важные для CleanYourTV критерии: folders/tags, sorting, sideloaded apps, более трёх элементов в row, App Info/Force Close, clock/date, no ads и минимальные permissions.

Это полезный snapshot discovery и пользовательских ожиданий, но не источник реализации. У gist нет обнаруженного LICENSE-файла; не копировать текст, структуру или внешние материалы без отдельной проверки. Ссылки: [gist](https://gist.github.com/denilsonsa/80cbb3a14b3bf63de75e6bf81c89ee05), [raw text](https://gist.githubusercontent.com/denilsonsa/80cbb3a14b3bf63de75e6bf81c89ee05/raw).

### 7. Plume Launcher — лучший референс компактного user journey

Plume сознательно сводит home screen к apps и Continue Watching. README и код показывают следующие паттерны:

- apps в одной row, сортировка по most used, hide без потери приложения из All apps;
- hold OK для rearrange/remove/pin, отдельные режимы отображения app names и icon style;
- Sources в верхней панели, HDMI-CEC name/logo, input no-signal state;
- remote remap с разными действиями для Press и Hold, при этом Back/OK/arrows/Home/Power/volume нельзя переназначить, чтобы не заблокировать пользователя;
- PIN lock только для изменения layout, не как ложная parental control;
- light/dark/automatic theme, собственные wallpapers и мягкий fade для читаемости;
- Continue Watching из Android TV Watch Next и каналов приложений;
- setup card “Finish setup” и явный путь Home button/default launcher.

Навигация реализуется через фокусируемый home UI и accessibility Home button service: [MainActivity.kt](https://github.com/aradhyas8/Plume_Launcher/blob/603302de53565891326447539d2d750e779d4516/app/src/main/java/dev/plume/MainActivity.kt), [HomeOverride.kt](https://github.com/aradhyas8/Plume_Launcher/blob/603302de53565891326447539d2d750e779d4516/app/src/main/java/dev/plume/HomeOverride.kt), [Remap.kt](https://github.com/aradhyas8/Plume_Launcher/blob/603302de53565891326447539d2d750e779d4516/app/src/main/java/dev/plume/Remap.kt), а визуальный glass/fade слой — в [Glass.kt](https://github.com/aradhyas8/Plume_Launcher/blob/603302de53565891326447539d2d750e779d4516/app/src/main/java/dev/plume/Glass.kt). Для CleanYourTV особенно ценны короткий first-run, удержание OK для опасных действий и безопасная модель remap.

Лицензия — [GPL-3.0](https://github.com/aradhyas8/Plume_Launcher/blob/603302de53565891326447539d2d750e779d4516/LICENSE). Логотипы, Material Symbols и изображения упоминаются в README с отдельным происхождением/лицензиями; их нельзя переносить как часть GPL-кода.

### 8. Arc Launcher — расширенный, более “launcher-first” вариант

Arc — fork LTvLauncher; README прямо указывает lineage и добавляет grid layout с configurable row/column sizing, Watch Next top carousel, custom categories, Left/Right reorder, quick status bar с time/data usage/Wi-Fi, auto-hide status bar, accent presets и multilingual UI. В отдельном слое — video wallpapers, slideshows из Unsplash/Reddit, dynamic wallpapers, OLED screensaver, sideloaded app support, in-app updater и experimental brightness scheduler.

Код подтверждает самостоятельные focus/navigation компоненты и категориальную модель: [flauncher.dart](https://github.com/meddouribadis/arclauncher/blob/58fca01519b5884ad6aa3c550019d6eb60818be4/lib/flauncher.dart), [apps_grid.dart](https://github.com/meddouribadis/arclauncher/blob/58fca01519b5884ad6aa3c550019d6eb60818be4/lib/widgets/apps_grid.dart), [category_row.dart](https://github.com/meddouribadis/arclauncher/blob/58fca01519b5884ad6aa3c550019d6eb60818be4/lib/widgets/category_row.dart), [custom_traversal_policy.dart](https://github.com/meddouribadis/arclauncher/blob/58fca01519b5884ad6aa3c550019d6eb60818be4/lib/custom_traversal_policy.dart). Настройки разделены на страницы wallpaper/status bar/watch next/application details, что полезно как модель progressive disclosure.

Для CleanYourTV применимы category/grid/row abstraction, auto-hide второстепенного status bar, устойчивый focus traversal, кастомные banners для неизвестных приложений и screen-burn-in protection. Video wallpaper, Reddit/Unsplash и brightness scheduler лучше оставить за пределами clean-up продукта. Лицензия — [GPL-3.0](https://github.com/meddouribadis/arclauncher/blob/58fca01519b5884ad6aa3c550019d6eb60818be4/LICENSE).

### 9. LTvLauncher — богатый набор функций и зрелые настройки

LTvLauncher ближе всего к “полноценному домашнему центру”: Continue Watching с recency sorting, weather/status bar, Wi-Fi/data usage, notifications, custom themes, app banners, HDMI/AV/component input selector, Home Button Fix для Google TV/Fire TV, OLED screensaver, audio feedback и backup/restore. README фиксирует четыре визуальных темы — Modern/Default, Premium, Classic, Capsule — и варианты row/grid.

В исходниках навигация явно моделируется: [flauncher.dart](https://github.com/leanbitlab-org/LtvLauncher/blob/c4ca7a9ce9a0880018014b35789fb879337040e8/lib/flauncher.dart) использует `FocusTraversalGroup` и row-by-row policy; [category_row.dart](https://github.com/leanbitlab-org/LtvLauncher/blob/c4ca7a9ce9a0880018014b35789fb879337040e8/lib/widgets/category_row.dart) и [apps_grid.dart](https://github.com/leanbitlab-org/LtvLauncher/blob/c4ca7a9ce9a0880018014b35789fb879337040e8/lib/widgets/apps_grid.dart) поддерживают горизонтальные rows, grids и reorder с восстановлением focus; [application_info_panel.dart](https://github.com/leanbitlab-org/LtvLauncher/blob/c4ca7a9ce9a0880018014b35789fb879337040e8/lib/widgets/application_info_panel.dart) собирает reorder/hide/remove-from-category/app-info в одном контекстном месте. [settings_panel.dart](https://github.com/leanbitlab-org/LtvLauncher/blob/c4ca7a9ce9a0880018014b35789fb879337040e8/lib/widgets/settings/settings_panel.dart) показывает отдельную навигацию по страницам настроек.

Для CleanYourTV стоит взять именно navigation engineering: фокус не должен прыгать после изменения списка, grid должен объяснять Up/Down/Left/Right, а опасные действия — открываться в контекстной панели с объяснением. Weather, notifications и live data usage не обязательны для MVP очистки. Лицензия — [GPL-3.0](https://github.com/leanbitlab-org/LtvLauncher/blob/c4ca7a9ce9a0880018014b35789fb879337040e8/LICENSE).

### 10. Material TV Launcher — сильный референс “использование вместо ручной настройки”

Material TV Launcher автоматически строит dock из шести наиболее используемых приложений, не hardcode-ит список и перестраивает его по мере изменения привычек. HDMI-CEC-устройства получают собственные названия вроде console, green on-dot и прямой switch input. Now Playing показывает artwork, track, wavy progress и play/pause, а equalizer отмечает активное приложение в dock.

Визуальная система необычно цельная: цвет берётся из banner приложения в focus, затем Material 3 dynamic color задаёт фон, shape и controls; focus увеличивает tile и даёт glow; есть spring motion, morphing shapes, top-bar strip и clock, чья typographic weight зависит от времени. [HomeActivity.java](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/src/com/rampey/materialtv/HomeActivity.java) связывает home/apps/settings, dock и HDMI; [Focus.java](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/src/com/rampey/materialtv/Focus.java) задаёт focus geometry; [Palette.java](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/src/com/rampey/materialtv/Palette.java) — palette extraction; [MediaListener.java](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/src/com/rampey/materialtv/MediaListener.java) — Now Playing access; [HomeKeyService.java](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/src/com/rampey/materialtv/HomeKeyService.java) — Home-button interception.

Для CleanYourTV применимы usage-based ordering, именованные CEC inputs, локальная privacy posture и аккуратный adaptive accent. Не нужно копировать анимации, exact shapes, Google Sans Flex или bundled color library без соблюдения их отдельных лицензий. Основная лицензия — [Apache-2.0](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/LICENSE); bundled dependency имеет свой [Apache license](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/third_party/material-color-utilities/LICENSE), шрифт — [SIL OFL](https://github.com/0xRampey/material-tv-launcher/blob/eccdc92a8688b535bf013e120d45a3c0fb1a0f90/assets/fonts/GoogleSansFlex-OFL.txt).

## Навигационные паттерны, которые стоит зафиксировать в CleanYourTV

### Основной экран

- Верхний уровень: выбранный ТВ, connection status, progress/health summary и одна primary action — “Review cleanup”.
- Первый ряд: рекомендуемые безопасные действия; второй — user-installed apps; третий — built-in apps; System/protected — отдельная сворачиваемая секция.
- `Left/Right` перемещает элемент внутри ряда; `Up/Down` меняет ряд; `OK` открывает detail; удержание `OK` открывает быстрый контекстный action sheet.
- После disable/restore/reorder фокус возвращается на тот же пакет или на ближайший видимый элемент, а не в начало списка.
- Back закрывает detail/action sheet, затем возвращает фокус на исходный элемент; destructive action никогда не выполняется по одному случайному нажатию.

### Review flow

1. Выбор профиля/списка для конкретной модели.
2. Группировка по риску и типу: safe candidate / review / protected.
3. Detail для каждого пакета: label, package name, origin, why recommended, what may break.
4. Итоговый diff с количеством изменений и предупреждением о необратимых действиях.
5. Execute с progress и возможностью отменить только ещё не начатые операции.
6. Result screen с Undo, Restore all и ссылкой на History.

### Визуальная система

Рекомендуемый baseline — тёмная поверхность с достаточным контрастом, один статусный акцент (green/amber/red), умеренный focus glow/lift и no-ad/no-recommendation layout. Адаптивный accent от выбранного устройства можно добавить позднее. Не смешивать одновременно glass, video wallpapers, multiple themes, weather и notification drawer в MVP: каждый слой повышает стоимость тестирования на реальных TV-пультах.

## Лицензионная карта

| Источник | Лицензия | Что это означает для CleanYourTV |
|---|---|---|
| Tellyscope | GPL-3.0 + [NOTICE](https://github.com/man15h/tellyscope/blob/a86cd362e87d884154a6a72d13b4f49643a3ad19/NOTICE) | Нельзя просто вырезать и закрыто распространять код; при производном распространении учитывать GPL и third-party notices |
| Monet Launcher | LICENSE отсутствует; source code отсутствует | Не копировать код/ассеты; использовать только абстрактные продуктовые идеи |
| Awesome list | CC BY-NC-SA 4.0 | Лицензия списка, не перечисленных приложений и не кода launcher |
| TV Launcher | GPL-3.0 | Производные изменения/распространение — с GPL-обязательствами |
| Android TV launcher | MIT | Разрешительно, но сохранить copyright/license notice; отдельные зависимости проверять отдельно |
| Gist | LICENSE не обнаружен | Не считать текст автоматически свободным для копирования; только ссылаться и пересказывать |
| Plume | GPL-3.0 | Copyleft для производных распространённых версий |
| Arc Launcher | GPL-3.0 | Учитывать fork lineage и copyleft |
| LTvLauncher | GPL-3.0 | Copyleft; не смешивать код с несовместимой закрытой лицензией |
| Material TV Launcher | Apache-2.0 | Разрешительно при сохранении notices; bundled code/fonts имеют отдельные лицензии |

Юридическая граница для реализации CleanYourTV: переносить идеи, требования и поведенческие принципы можно реализовать собственной архитектурой и собственным кодом; нельзя переносить исходники, exact UI assets, тексты, логотипы и зависимости без проверки соответствующей лицензии и NOTICE. Для GPL-источников особенно безопасный путь — не копировать код, а написать независимую реализацию safety/workflow по собственному доменному контракту.

## Источники-срезы

Для воспроизводимости проверенные GitHub snapshots: Tellyscope `a86cd362e87d884154a6a72d13b4f49643a3ad19`; Monet `a6a213c5e6a80067ab3d5c633b2eb54e4cc20b00`; Awesome list `9f0c751ff58b609cee1c482d4634c53c250f266`; TV Launcher `a0149305678b243e18cd573c0268a99683ee9558`; Android TV launcher `e5f5ed2c33abb0cc61393b5451c45d6c85f23686`; Plume `603302de53565891326447539d2d750e779d4516`; Arc `58fca01519b5884ad6aa3c550019d6eb60818be4`; LTv `c4ca7a9ce9a0880018014b35789fb879337040e8`; Material TV Launcher `eccdc92a8688b535bf013e120d45a3c0fb1a0f90`.
