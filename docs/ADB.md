# Wireless ADB: from the first APK to a connection

English | [한국어](ADB.ko.md)

ADB connects a development PC to Android on the glasses for app installation, commands, file transfer and logs. This guide records a working wireless setup using a settings-launcher APK, without a development cable.

## 1. Install the first APK

1. Build `dist/adb-helper-android-debug.apk` using [development setup](DEVELOPMENT.md), then copy it to your phone.
2. In Hi Rokid, open **Home → Toolbox → Glasses App Management** and install the APK **on the glasses**. Installing it on the phone opens the phone's settings instead. Menu names can vary by version/language.
3. Launch **Rokid ADB Helper** on the glasses. The buttons open Android settings, device information, Wi-Fi and developer options. The current app labels are Korean: **Android 설정**, **기기 정보**, **Wi-Fi 설정**, **개발자 옵션**.

## 2. Enable developer options

On the tested device, only the Developer options button initially failed to open. Other settings pages were available. This sequence enabled it:

1. In Helper, open **기기 정보 (Device info)**.
2. Tap **Build number / 빌드 번호** seven times and confirm the developer activation message.
3. Return to Helper and open **개발자 옵션 (Developer options)**.
4. Enable **Wireless debugging**. Tap the setting's label, separately from its toggle, to open its details.

Hi Rokid's glasses ADB toggle and Android's Wireless debugging setting are separate. An IP address or a connected charging cable does not establish ADB access. This procedure is verified on one device, not every model or firmware.

## 3. Prepare the PC and pair

Use [official Platform Tools](https://developer.android.com/tools/releases/platform-tools). Connect the glasses and PC to the same router/LAN; the PC may be wired. Guest networks or client isolation can block discovery/connections.

```powershell
adb version
adb devices -l
adb mdns services
```

On the glasses, open **Pair device with pairing code** in Wireless debugging. Keep that screen open; it provides a pairing IP, port and six-digit code.

```powershell
$pairEndpoint = Read-Host 'Pairing IP:port from the glasses'
adb pair $pairEndpoint
# Enter the code from the glasses at the prompt.
```

`Successfully paired` confirms authentication. Do not put the code in command arguments, files, Git or screenshots. If it expires, reopen the dialog and use the new code and port.

## 4. Connect and identify the device

Pairing may trigger automatic connection. Otherwise, use the connection IP:port on the main Wireless debugging page or the **_adb-tls-connect._tcp** service from `adb mdns services`. The **_adb-tls-pairing._tcp** service is for pairing, not connection.

```powershell
$deviceEndpoint = Read-Host 'Connection IP:port from the glasses'
adb connect $deviceEndpoint
adb devices -l
adb -s $deviceEndpoint shell getprop ro.product.model
adb -s $deviceEndpoint shell getprop ro.build.version.release
adb -s $deviceEndpoint shell getprop ro.build.version.sdk
```

Pairing and connection ports can differ. Do not assume port 5555. IPs and ports can change after network or wireless-debugging restarts. Confirm `device` state and the model before installing or writing files.

The tested device reports **Rokid RG-glasses, Android 12 / API 32**. Real IPs, MACs, serials, service identifiers and pairing codes are not recorded here.

## 5. Why adb devices can show two entries

A manual IP connection and an mDNS automatic connection can register separate transports to the same device. This example does not identify a real device:

```text
192.0.2.10:35000                           device
adb-EXAMPLE._adb-tls-connect._tcp          device
```

For the tested glasses, model and internal serial comparisons in memory confirmed the same physical device. Raw identifiers were not saved. Two entries alone do not prove that they always represent one device.

Commands without a target may fail with `more than one device/emulator`. Use **`-s`** with one complete first-column value from `adb devices`: either IP:port or the mDNS name.

```powershell
./scripts/adb-info.ps1 -Serial $deviceEndpoint
adb -s $deviceEndpoint install -r ./dist/gpt-viewer-android-debug.apk
```

To remove a manual connection, run `adb disconnect $deviceEndpoint` and inspect the list again. If the mDNS entry remains, it can be used with `-s`. Automatic reconnection can change the list; specifying a target is more reliable than trying to force one entry. No global PC mDNS setting needs to be changed.

## 6. Read-only information helper

```powershell
./scripts/adb-info.ps1 -Serial $deviceEndpoint
```

It reads model, manufacturer, Android version and API only. The Serial parameter takes the first column from `adb devices`; it does not require discovering the hardware serial. If multiple transports exist and no target is supplied, it stops. It does not install apps, transfer files, change settings, restart the ADB server or write logs.

## 7. Disconnect and reconnect

After use, disconnect the PC transport and turn off Wireless debugging on the glasses. `adb disconnect` does not turn off the device setting. For the next session, enable Wireless debugging and check its current connection endpoint.

**A dropped connection does not necessarily erase pairing.** A retained pairing may reconnect without a new code. Factory reset, revoked authorization or changed PC keys can require pairing again. An `offline` or missing transport alone is not proof that pairing was lost.

## Helper boundaries

Helper requests public Android Settings actions only. It does not automatically enable ADB, write settings, use root/accessibility/hidden APIs, open ports or collect codes. It declares no permissions and displays model/Android version only. It does not infer ADB status from settings values that may be restricted for third-party apps.

Missing or denied settings screens are reported. Availability, appearance and input depend on firmware. This APK cannot remove system restrictions.

## Official references

- [Enable Android developer options](https://developer.android.com/studio/debug/dev-options#enable)
- [Wireless ADB and target selection](https://developer.android.com/tools/adb)
- [Settings actions](https://developer.android.com/reference/android/provider/Settings#ACTION_APPLICATION_DEVELOPMENT_SETTINGS)
- [ADB mDNS architecture](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/adb_wifi.md)
- [Rokid Toolbox](https://global.rokid.com/pages/faq)
