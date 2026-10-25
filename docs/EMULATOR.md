# Local Android lab

English | [한국어](EMULATOR.ko.md)

Rokid Android Lab is strictly a PC virtual-development environment. It runs the actual APK in an AOSP API 32 x86_64 VM and hosts the native emulator screen inside the panel. It does not pair with, query, synchronize with or control real glasses or a phone. Installing the finished APK on hardware is a separate workflow.

## Layout and daily use

```powershell
python tools/emulator.py
```

- **Above the screen:** Start and Stop.
- **Below the screen:** app selection, Build & run, Run APK, Send file, and the permanent direction/Enter/Back buttons.
- **Right side:** Lab and App log tabs. The divider can be dragged to resize the log area.
- **Lab:** operation output plus Check, Setup and Display settings.
- **App log:** recent logs for the selected app, Refresh and Auto. Auto refresh runs while the tab is visible and the virtual emulator is attached. It shows a bounded recent snapshot, not an unlimited archive. A stopped/crashed app may need separate debugger inspection.

Use the mouse/trackpad directly in the embedded screen for pointer movement, click/double-click and horizontal/vertical scrolling, or use the buttons below it. There is no Input mode selector. When testing a buttons-only workflow, use directions to move focus before Enter. Tab/Page shortcuts remain CLI-only development aids and are not required app controls.

Choose Start, wait for Android to boot, select the app, then Build & run. This runs the app's build/lint checks before installation and Activity launch; Run APK skips the build. Setup and Check are in the Lab tab for initial preparation/diagnostics and are not daily startup steps.

Native hosting uses Windows APIs without extra Python packages. Startup can briefly show an SDK window before attachment. Screen aspect ratio is preserved when resizing. If an existing VM was started headless, stop it and start it from the panel to obtain a native display.

Stop closes only the owned VM. Closing the panel waits for its current operation, then stops its attached VM. Saved apps/files remain. If SDK shutdown fails, the native window is detached before the panel is destroyed. No wipe, automatic uninstall or data reset is performed.

## Local display settings

The initial display is **provisional 480 × 640, 160 dpi, font scale 1.0**. It is not a measurement read from glasses.

Stop the VM, open **Lab → Display…**, enter width/height/density/font scale, and choose Apply locally. Start again to apply. API remains 32. These values are stored only in ignored `.emulator/display.local.json`. Existing local numeric display values from an older version are preserved as manual settings; no device is contacted to migrate them.

There is no real-device capture button, CLI capture command or device/IP input. The Lab controls only its SDK-owned virtual transport. Internally it uses a dedicated loopback ADB server on port 5039 and a VM console port of 5586. Wireless auto-connect is disabled and the server's USB filter excludes normal physical devices. It never issues connect/pair commands or restarts the normal PC ADB server. These ports are internal PC details, not a glasses endpoint.

The VM cannot reproduce Rokid firmware/services, optical characteristics, physical Bluetooth peripherals, camera/NPU drivers or real battery behavior. PC VM timing/memory/power are not hardware measurements. Future NDK modules require a VM x86_64 build as well as the actual device ABI outside this Lab. Future physical-device integration must stay outside the Lab; use mocks here.

## Send file

Send file accepts a regular file and copies it to Android `/sdcard/Download/` using its original filename. If a name exists, a numbered filename is used. The file is not automatically opened or installed. Use a file manager or the app file picker → internal storage → Download. In Paper Viewer, use PDF 열기.

There is no PDF-only transfer restriction. Receiving apps retain their own format/size limits; Paper Viewer still accepts only PDFs up to 200 MiB. Older app-folder PDFs are left in place without migration or deletion. Transfer is to the VM only and does not publish a file or send it to real glasses.

VM disks, documents, display settings, logs and screenshots remain private under ignored `.emulator/`. Do not publish that folder. Signature-key mismatches are reported instead of uninstalling an app and losing its data.

## Terminal and checks

Use Windows, Python 3.10+ with Tk, Java 17 and the SDK configuration in [development](DEVELOPMENT.md). Existing ignored `toolchain.local.json` supplies local paths. No additional repository folders, Python packages, account or vendor SDK are needed.

```powershell
python tools/emulator.py doctor
python tools/emulator.py setup
python tools/emulator.py display --width 480 --height 640 --density 160
python tools/emulator.py start
python tools/emulator.py run paper-viewer --build
python tools/emulator.py file "C:/MyFiles/example.txt"
python tools/emulator.py logs paper-viewer
python tools/emulator.py stop
```

CLI-only start runs the SDK independently; open the default GUI for the integrated view. `start --headless` supports automated virtual validation. All device operations reject physical transports and verify the online qemu instance and owned AVD name. Source checks are `python -m unittest discover -s tests -v` and `python scripts/check.py`. See [validation](VALIDATION.md) for local evidence. Current work is local for review; no push is implied.

Official references: [Android Emulator](https://developer.android.com/studio/run/emulator-commandline), [ADB command options](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/docs/user/adb.1.md), [wireless auto-connect configuration](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/android16-s2-release/adb_mdns.cpp), [Windows native hosting](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent).
