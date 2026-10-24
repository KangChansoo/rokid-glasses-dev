# PDF transfer and file management

English | [한국어](FILE_TRANSFER.ko.md)

AnExplorer is an **optional third-party file manager**, not part of Paper Viewer. PDF reading does not require its Pro license. Do not confuse phone-to-glasses transfer with the viewer's current internal-copy behavior.

## Install and allow file access

Use the [publisher's glasses download page](https://anexplorer.io/download/glasses). The tested download was AnExplorer 6.0.8, from the APK linked by that page. This repository does not redistribute it.

1. Save the single APK on your phone, then install it **on the glasses** through **Hi Rokid → Home → Toolbox → Glasses App Management**. This does not require a working ADB connection.
2. Open AnExplorer on the glasses. Use its file-access request, or Helper → Android settings → Apps → Special app access → All files access → AnExplorer, to enable file management access. Menu names can vary.
3. If you later want AnExplorer to install other APKs, separately allow **Install unknown apps** for it. That is a different setting from PDF file access. Root is not required for ordinary shared documents.

The all-files permission belongs to AnExplorer, not this repository's APKs. Android can still restrict other apps' Android/data directories. Prefer ordinary shared documents rather than trying to bypass those restrictions.

## Phone to glasses

With AnExplorer on both devices and both on the same Wi-Fi:

1. On the glasses: **Home → Connect → Transfer → Receive**.
2. On the phone: **Connect → Transfer → Send**, select the PDF and choose the receiving glasses.
3. On the glasses, look in **Transfer → Received Files**. The publisher documents `/AnExplorer/Received/` as a default; actual location can vary by version/settings.
4. Long-press the PDF and select **Open with → Paper Viewer APK**. A normal tap may open AnExplorer's own viewer instead.

`Documents/Papers` is an optional organization folder. It is not required for Open with. The app-owned folder and Android picker are described in [app usage](APPS.md).

## Trial and paid features

The installed app displayed **7 days remaining in the AnExplorer Pro trial**. [The official FAQ](https://anexplorer.io/questions) describes a free base app; [the pricing page](https://anexplorer.io/pricing) lists Wi-Fi sharing and Connect among Pro features. The exact free transfer behavior after the trial is **not verified**, and the publisher's pages do not establish a consistent feature boundary. Do not treat wireless transfer as permanently free based on the trial.

The trial banner alone does not establish whether a paid subscription was registered. Check the actual purchase/subscription status before relying on billing assumptions. This project does not initiate purchases or manage AnExplorer licensing.

AnExplorer Pro is not a dependency of Paper Viewer: its existing private PDF copy is rendered by our app independently. Alternative transfer methods can be used without changing the PDF renderer. No feature bypass or license workaround is part of the project.

## Alternative: explicit-target ADB

An already authenticated ADB connection can copy a PDF to shared storage. Enter your own current endpoint and file path; neither is saved in the repository.

```powershell
$deviceEndpoint = Read-Host 'Connection IP:port'
$pdfPath = Read-Host 'Local PDF path'
adb -s $deviceEndpoint shell getprop ro.product.model
adb -s $deviceEndpoint shell mkdir -p /sdcard/Documents/Papers
adb -s $deviceEndpoint push $pdfPath /sdcard/Documents/Papers/
```

Check the model before writing. `adb push` can overwrite an existing same-named file: choose a new filename or check the destination first if needed. This alternative is not required when transferring through a file manager. Use the current address and [ADB reconnection guidance](ADB.md), not a fixed port.

Do not upload private PDFs, extracted content or screenshots containing papers to GitHub or a cloud service. Use the synthetic demo for public visual examples.

References: [publisher's transfer guide](https://anexplorer.io/transfer/android-to-android), [Android all-files access](https://developer.android.com/training/data-storage/manage-all-files).
