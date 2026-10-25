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

The previous read-only ADB script returned model/API for an explicit target and refused an unspecified target when two transports were present. GitHub Actions is configured; local checks and server-side CI results are separate.

| APK | Bytes | SHA-256 |
|---|---:|---|
| `gpt-viewer-android-debug.apk` | 19904 | `afdbb89ac661df271eccdf969db10953698a9f0fd750366cf1adc73d6c13c099` |
| `paper-viewer-android-debug.apk` | 51344 | `3a13889d6872e5b36f3632ec84e3d5ffd44d569cc70d0724da158cd3c40e5712` |
| `adb-helper-android-debug.apk` | 23732 | `884084ba34c3d5cc47113b4d867fe74219d2ff4b0cfbd8d824a89ee206d70a37` |

These hashes describe that build, not every future APK. Current local build output is recorded in ignored `dist/artifacts.json`.

## Repository layout verification

The app modules now live under `apps/`, with `shared/android-ui/` for common UI and the Gradle wrapper/settings at the root. Generated files use `build/<module>/`. All 16 Java/XML source files are byte-identical to the previous layout, and the three project APK hashes still match the table above.

The root build passed assembleDebug and lintDebug for all three apps and four Paper Viewer JVM tests. Current lint reports have zero errors and three warnings per app; they cover the selected Gradle version, orientation assumptions and prototype strings. After removing the old layout, `./scripts/build.ps1 -App paper-viewer` also passed independently. These are build checks, not another glasses usability test.

`dist/` now contains flat APK files and a single `artifacts.json`. The build verifies hashes, package/SDK metadata, permissions, backup exclusions, signatures and alignment. The existing external AnExplorer APK is unchanged and marked `external`; its permissions are separate from this project's zero-permission apps. `adb-info.ps1` was removed in favor of the explicit-target standard commands in the [ADB guide](ADB.md).

## PC Android lab verification

The isolated AOSP API 32 x86_64 AVD booted with WHPX acceleration. It reported 480 × 640 and 160 dpi, matching the **provisional lab profile**, not a display measurement from the glasses. No physical device was connected during this validation. No Windows feature or reboot command was used.

Ten Python tests passed for display parsing/validation, read-only capture without saved identifiers, and refusal to install or send input to physical, unrelated or ambiguous emulator targets. Documentation/JSON/XML checks covered 33 files. The Python panel layout was inspected on Windows.

The real project APKs were installed and launched in the VM. GPT Viewer passed Page Up/Down, Next tap and single Enter activation after Tab focus. Paper Viewer passed generated-demo rendering, paging, transfer of that generated PDF to the app folder, import and zoom. ADB Helper launched without changing settings. A selected-app log snapshot was readable. The Python Build & run command also passed Paper Viewer's existing build, lint and four JVM tests before installation/launch.

Only the app's generated three-page demonstration PDF was used; no real paper was transferred. Runtime screenshots, VM disks and logs are private in ignored .emulator/ and are not published. These checks do not establish Rokid firmware, temple/watch/Bluetooth input, optics, ARM/native ABI compatibility or hardware performance. Capturing real display values and checking representative flows on the glasses remain pending.

## Separate input-mode checks

The user clarified two available modes: Touchpad (pointer, click/double-click and two-finger horizontal/vertical scroll) and Buttons (four directions, Enter, Back). The panel now selects these modes separately; Tab/Page shortcuts and optional physical-device ADB capture are hidden under Advanced PC tools by default. These are reported device capabilities, not measured firmware event mappings.

On the owned API 32 VM, GPT Viewer passed directional focus, Enter page actions and Back using only the six Buttons-mode keys. Paper Viewer passed directional button focus, next page, zoom and Back with the existing generated demo. No Tab/Page keys or mouse were used in these routes. Touchpad gesture fidelity and buttons-only PDF panning remain unverified/unimplemented respectively. No app source or APK changed for this panel/documentation update.

## Integrated Lab local review

The SDK's native Android display was hosted inside the Python Lab on Windows, with app/file controls and the two input modes below it. Live Android/app rendering and aspect-preserving layout were observed. This uses the native SDK window, not a reconstructed app UI or a screen-copy mock. Transient SDK startup windows are ignored until a matching native window is available; startup can briefly show a standalone SDK window. Windows DPI/SDK differences still need broader testing.

Sixteen Python tests passed, including generic-file validation, Unicode/quoted filenames, collision names, failed-push reporting and native-window identity. A generated text file with spaces and an apostrophe was sent to Download twice and pulled back byte-for-byte; the second transfer used a numbered filename. Only these generated test files were cleaned up. The user's running document and existing app-folder PDFs were not migrated, deleted or published. No Android app source or APK was changed for this local tooling update.

This work is on a local feature branch for review. No commit, shared-branch merge or push was performed for it. VM data, documents, screenshots and logs remain excluded from Git.

## Virtual-only Lab and log tabs

The current Lab removes physical-device capture completely. Width, height, density and font scale are manual local settings. Device commands reject physical transports and host connect/pair/tcpip operations. A private loopback ADB server uses port 5039, disabled mDNS auto-connect and a virtual-only USB filter; the owned VM uses console port 5586. The ordinary PC device server is not restarted or reused.

Twenty Python tests passed. The VM booted on the private channel and the sample GPT APK launched; its selected-process log was read successfully. On Windows the right-side Lab/App log tabs, populated App log view, Start/Stop above the screen, permanent navigation buttons and absence of an Input mode selector were inspected. Native positioning was corrected after SDK startup and unnecessary upscaling was avoided to prevent clipping at the tested profile. No hardware endpoint was used and no Android app source changed. This remains local uncommitted work; no merge or push was performed.

## Still pending

GPT Viewer device display/input; complete PDF picker/provider and original-access behavior; panning/zoom/navigation/resume; fonts/long documents; per-app temple/watch/phone control; controlled power/memory/latency measurements. There is no live API, phone companion, camera AI or C/NDK processing yet.

Current PDF opening always makes one internal copy. Direct read-only original access is a plan, not a completed fix. No development cable purchase or paid API request was made during these checks.
