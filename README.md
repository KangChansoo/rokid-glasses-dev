# Rokid Glasses Dev

English | [한국어](README.ko.md)

An ongoing personal project to develop Android apps for **Rokid AI Glasses** and explore **embedded systems and AI** through hands-on development.

A custom PDF viewer prototype is running on the glasses. Current work focuses on readability, navigation and file handling. Native C/NDK processing, smartphone integration and AI applications are future goals.

## Progress

- [x] Use a Galaxy Watch as a remote controller
- [x] Set up wireless ADB
- [x] Set up AnExplorer for file management
- [ ] Develop a PDF viewer
- [ ] Develop a GPT viewer
- [ ] Develop C/NDK modules
- [ ] Add smartphone integration
- [ ] Measure memory usage, latency and power consumption
- [ ] Explore camera and AI applications

Viewer prototypes exist; the unchecked viewer items represent ongoing development. AnExplorer is an optional third-party tool: the installed app shows a 7-day Pro trial, and continued free wireless transfer is not verified. See [file transfer](docs/FILE_TRANSFER.md).

## What works today

| Component | Current state |
|---|---|
| ADB Helper | Installed on the glasses; opens Android settings. Developer options enabled through Build number. |
| Wireless ADB | Pairing, authenticated connection and device information confirmed on Rokid RG-glasses / Android 12 / API 32. |
| Galaxy Watch7 / WearMouse | Bluetooth remote input established; compatibility with every viewer control still needs validation. |
| Paper Viewer | Actual PDF page rendering confirmed on the glasses. Reading UI and file handling remain prototype-level. |
| GPT Viewer | Built with sample responses; live AI integration and device validation are pending. |

Current apps use **Java and standard Android APIs**. There is no C/NDK processing, camera AI, phone companion or live API integration yet. GPT Viewer does not access existing ChatGPT conversations.

## Get started

1. Follow [development setup](docs/DEVELOPMENT.md) and run `./scripts/build.ps1`.
2. Copy `dist/adb-helper-android-debug.apk` to your phone and install it **on the glasses** through **Hi Rokid → Home → Toolbox → Glasses App Management**. Labels may vary by app language/version.
3. In Helper, open **기기 정보 (Device info) → Build number**, tap it seven times, return to **개발자 옵션 (Developer options)**, then enable Wireless debugging.
4. Use the glasses' current pairing/connection endpoints in the [ADB guide](docs/ADB.md).
5. Follow [app usage](docs/APPS.md) and [PDF transfer](docs/FILE_TRANSFER.md) to test a document you own. No special folder is required when opening through a file manager.

## Repository

```text
apps/
  adb-helper/            Android settings launcher
  gpt-viewer/            Hello World / sample-response viewer
  paper-viewer/          Local PDF page viewer
shared/android-ui/      Shared green-on-black Android UI
gradle/                 Gradle wrapper; build settings live at the root
scripts/
  build.ps1              Build one app or all apps; update artifacts.json
  check.py               Markdown links, JSON and XML checks
docs/                    English and Korean guides
measurements/            Empty battery and input measurement templates
build/                   Generated files, grouped by module (Git-ignored)
dist/                    Flat APK folder + artifacts.json (Git-ignored)
```

APK output, real papers, extracted text, device identifiers, private screenshots, ADB keys, API keys and signing keys are excluded from Git. PDF files are not bundled. The current viewer creates one private PDF copy; opening originals directly is a planned improvement, not an implemented feature. See [security](SECURITY.md).

## Guides

- [Wireless ADB](docs/ADB.md)
- [File transfer and AnExplorer limitations](docs/FILE_TRANSFER.md)
- [Development and builds](docs/DEVELOPMENT.md)
- [Apps and current limitations](docs/APPS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Validation record](docs/VALIDATION.md)
- [Roadmap](docs/ROADMAP.md)
- [Battery measurements](docs/BATTERY.md)

Independent project; not affiliated with Rokid, OpenAI, WearMouse or AnExplorer. Third-party software retains its own terms.
