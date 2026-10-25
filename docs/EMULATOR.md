# Local Android lab

English | [한국어](EMULATOR.ko.md)

Develop and debug the actual APK on a PC, then use the glasses for hardware and final usability checks. The Python control panel runs our apps on an isolated Android Emulator AVD. It does not contain a Rokid firmware image.

## Environment fidelity

| Aspect | Lab behavior |
|---|---|
| Android API | API 32, matching the observed glasses API; AOSP Android 12L x86_64 image. |
| APK | The same project debug APK, native Android UI and PDF renderer. |
| Display | Can read current pixel size, density and font scale from an explicitly selected connected device. |
| Initial display | **Provisional 480 × 640, 160 dpi, font scale 1.0. These values have not been measured on the glasses.** |
| Mouse / keys | Emulator mouse input plus Android Back, Enter, Tab, arrows and Page Up/Down. These are not verified mappings of the Rokid temple or Galaxy Watch. |
| Hardware | No Rokid OS/services, optical display, Bluetooth-device behavior, camera/NPU driver or physical battery model. |
| Performance | PC emulator CPU, GPU, RAM and storage differ. Do not treat its timing/memory/power results as glasses measurements. |

The lab uses 2 GB of RAM and a 2 GB userdata partition for PC convenience; these are not measured glasses specifications. A future C/NDK module will need an x86_64 build for this VM and the appropriate device ABI for the glasses. Passing here does not establish native hardware compatibility.

## Start

Use Windows, Python 3.10+ with Tk, Java 17 and the SDK setup in [development](DEVELOPMENT.md). The existing ignored `toolchain.local.json` supplies Java/SDK paths. No Python packages, web server, vendor SDK or account are required.

```powershell
python tools/emulator.py
```

In the panel:

1. **Setup** installs missing official Emulator / API 32 AOSP x86_64 packages and creates only the lab AVD. Downloads can take several minutes. Unaccepted SDK licenses must be reviewed with the official SDK tools; the lab does not accept new licenses automatically.
2. **Check environment** checks VM acceleration. On Windows, use Windows Hypervisor Platform if needed; enabling the Windows feature may require an administrator and restart. The tool does not change Windows features or reboot the PC.
3. **Start emulator** opens a separate emulator window and checks Android boot completion and display settings.
4. Select an app and choose **Build & run**. This runs that app's existing build/lint checks, installs it and launches its Activity. **Run existing APK** skips the build.
5. Use the mouse in the emulator window, the panel's Android key buttons, and **App logs**. Use Tab/arrows to focus a control before Enter. Logs are a bounded snapshot for the selected running app; stopped/crashed process logs may need Android Studio Logcat.
6. **Stop emulator** closes only the lab VM. Closing the Python panel alone leaves the emulator running.

If installation fails because a prior APK has a different signing key, resolve the key mismatch explicitly; the tool never automatically uninstalls apps or clears data. Android Studio can open the repository root and target this running emulator for debugging.

## Match the glasses display

Reconnect wireless ADB as described in [ADB](ADB.md). Click **Read glasses display** and supply the exact first-column target from `adb devices`. This operation only reads state, API, size, density and font scale. It stores a whitelist of display values locally; no IP, serial, pairing code or account is saved.

Stop/start the lab VM after capture. If it is already stopped, Setup can apply the new configuration before Start. A different captured API is rejected instead of silently pretending to match it. Display capture does not reproduce vendor fonts, optics, input firmware or system services.

## PDFs and local data

**Send PDF** puts a deliberately selected PDF in the emulator Paper Viewer app folder as `lab-document.pdf`. It replaces the previous file of that name. Open **앱 폴더** inside Paper Viewer to select it. This transfer is for the emulator only; it does not upload a paper to GitHub, a server or the real glasses. The viewer's existing internal-copy behavior is unchanged.

All lab AVD configuration, VM disks, test PDFs, display capture and emulator logs stay in ignored `.emulator/`. Do not publish that folder or its screenshots/logs. Its VM data persists across normal restarts. The tool does not use wipe/reset commands. Removing VM data manually would remove its installed apps and documents.

## Terminal commands

```powershell
python tools/emulator.py setup
python tools/emulator.py doctor
python tools/emulator.py start
python tools/emulator.py run paper-viewer --build
python tools/emulator.py key page-down
python tools/emulator.py logs paper-viewer
python tools/emulator.py stop
```

`capture --serial <target>` reads a specifically selected device. `pdf <path>` transfers a selected PDF to the lab. `start --headless` is available for automated validation. Every install/input/file-transfer/stop command verifies an online emulator transport, the virtual-device property and the lab AVD name. Physical glasses and unrelated AVDs are not write targets. It does not restart the global ADB server.

Run the PC tooling checks with `python -m unittest discover -s tests -v` and `python scripts/check.py`. The CI source job runs these checks without downloading or booting a VM. Runtime boot/rendering evidence is recorded separately in [validation](VALIDATION.md).

Official references: [Android Emulator](https://developer.android.com/studio/run/emulator-commandline), [AVD profiles](https://developer.android.com/studio/run/managing-avds), [hardware acceleration](https://developer.android.com/studio/run/emulator-acceleration). The implementation uses the SDK's installed emulator/avdmanager tools; current documentation also describes their newer Android CLI replacements.
