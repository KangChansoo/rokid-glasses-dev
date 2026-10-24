# Validation record — 2026-10-24

English | [한국어](VALIDATION.ko.md)

## Device evidence

- Installed and ran Rokid ADB Helper through Hi Rokid Toolbox.
- Android settings/device information opened; Developer options initially did not. Tapping Build number seven times enabled the developer page.
- Enabled Wireless debugging and completed PC pairing/authenticated connection. Read Rokid `RG-glasses`, Android 12 / API 32 after confirming `device` state.
- Compared the manual-IP and mDNS transports in memory and confirmed the same physical glasses. Raw identifiers, endpoints and codes were not stored in the repository.
- Galaxy Watch7 / WearMouse Bluetooth remote input was established. This is not full per-app input qualification.
- Installed AnExplorer and completed file-permission setup. The app displayed a 7-day Pro trial; post-trial transfer availability is not verified.
- The user reported a real PDF opening in Paper Viewer and provided a device screenshot showing document content and a 3.2x zoom state. This confirms rendering, not full reading usability, input mappings or restoration reliability.
- The PDF screenshot contains a real paper and private surroundings, so it is not published here.
- User-supplied versions: glasses `1.27.009-20261014-150203`, Hi Rokid `G1.15.6.1012`. These observations do not establish all-firmware compatibility.

## Build evidence

All three apps passed assembleDebug and lintDebug; Paper Viewer passed four JVM unit tests. APK package/launcher, min/target SDK, zero declared permissions, backup exclusions, signatures and zip alignment were checked. No PDF/key files or credential patterns were bundled.

The fresh repository build executed 179 Gradle tasks. Lint reported 0 errors for each app: three warnings each for GPT/Paper Viewer and two for Helper (portrait assumptions and, for viewers, untranslated prototype strings). Python source-metadata checks passed; the original run covered 20 Markdown/JSON/XML files. Later documentation adds files without changing APKs.

The read-only ADB helper returned model/API for an explicit target and refused an unspecified target when two transports were present. GitHub Actions is configured; local checks and server-side CI results are separate.

| APK | Bytes | SHA-256 |
|---|---:|---|
| `gpt-viewer-android-debug.apk` | 19904 | `afdbb89ac661df271eccdf969db10953698a9f0fd750366cf1adc73d6c13c099` |
| `paper-viewer-android-debug.apk` | 51344 | `3a13889d6872e5b36f3632ec84e3d5ffd44d569cc70d0724da158cd3c40e5712` |
| `adb-helper-android-debug.apk` | 23732 | `884084ba34c3d5cc47113b4d867fe74219d2ff4b0cfbd8d824a89ee206d70a37` |

These hashes describe that build, not every future APK. Current local build output is recorded in ignored `dist/android-apk-checksums.json`.

## Still pending

GPT Viewer device display/input; complete PDF picker/provider and original-access behavior; panning/zoom/navigation/resume; fonts/long documents; per-app temple/watch/phone control; controlled power/memory/latency measurements. There is no live API, phone companion, camera AI or C/NDK processing yet.

Current PDF opening always makes one internal copy. Direct read-only original access is a plan, not a completed fix. No development cable purchase or paid API request was made during these checks.
