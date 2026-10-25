# Rokid Glasses Dev

Develop standalone Android APKs under apps/. Iterate in the PC emulator, then transfer/install APKs through Hi Rokid Toolbox or AnExplorer. Physical wireless ADB is optional for diagnostics. Keep existing apps independent. Follow apps/AGENTS.md.

- This is a fresh Android-focused workspace. Do not add agent-studio frameworks, approval-only SDKs, undocumented APIs or old experiments to the default path.
- Java is the minimal Android UI boundary. Prefer portable C via NDK/JNI for meaningful processing when requested; use Python for PC tooling and experiments. C processing is not implemented yet.
- Phone-side CXR-L is a future optional integration, not a dependency of the current APKs. Verify official contracts before implementation.
- Never commit real papers, extracted document text, conversations, account data, IP/MAC/serials, pairing codes, ADB keys, tokens, private logs, APKs or signing keys.
- Use an explicit adb -s target when more than one transport is present. A manual IP connection and an mDNS service can represent the same physical device. Never choose a write target merely by list order.
- Preserve native Android Back/mouse/Enter behavior. Do not silently add permissions or broad storage access.
- For source/docs run python scripts/check.py. For Android changes run scripts/build.ps1 (assemble/lint all apps and Paper Viewer unit tests); inspect final APK manifests and signatures.
- Record build checks and hardware observations separately. ADB Helper, wireless ADB and PDF page rendering have device evidence. GPT device display, complete input mappings, PDF usability/restoration and controlled performance measurements still need validation.

- User-facing documentation is English by default with complete .ko.md siblings and reciprocal language links. Update both versions together. App UI localization is separate.

- Apps are independent modules in apps/; shared Android UI is shared/android-ui/. The apps/AGENTS.md safety/resource rules also apply to that shared module. Gradle settings/wrapper are at the repository root; generated output is root build/.
- dist/ is a flat, Git-ignored APK folder. scripts/build.ps1 creates its single artifacts.json with hashes, package metadata and validation. Mark external APKs as external; do not bundle or re-sign them.

## Branch workflow

- `main` is the release branch; `dev` integrates development work.
- Start every new app, feature, fix or documentation change from up-to-date `dev` on a `feature/<name>` branch. Use the app name or a short task name, for example `feature/paper-viewer` or `feature/paper-viewer-navigation`.
- Commit work on the feature branch, run the relevant checks, then merge it into `dev`. Never work directly on `main`; keep development commits off `dev` until they are integrated from a feature branch.
- Promote tested `dev` to `main` only for a user-authorized release. Ordinary development requests do not authorize a release merge. Preserve history; do not reset or force-push shared branches.
- After integrating a finished feature, leave the local checkout on `dev`. Create the next feature branch before editing again. Keep English and Korean workflow documentation aligned.

## Local emulator tooling

- tools/emulator.py is a Windows Python control panel/CLI for an isolated AOSP API 32 lab, not a Rokid firmware simulator. The Lab is strictly virtual-only and never pairs with, queries or controls real glasses/phones. Display values are local/manual and must not be claimed as measured hardware values.
- Keep VM disks, local display settings, PDFs, emulator logs and screenshots under ignored .emulator/. Never commit these artifacts or save raw device identifiers in a profile.
- No physical-device capture/connect/pair path is allowed. All install/input/transfer/stop operations must verify an online emulator transport, qemu property and exact owned AVD name. Never fall back to a physical or unrelated target, reset the global ADB server or automatically uninstall/clear data.
- Run python -m unittest discover -s tests -v and python scripts/check.py for tooling changes. Verify real VM boot/app flows when available; distinguish PC emulator evidence from physical-glasses verification and performance.

- User-confirmed input modes are separate: Touchpad (pointer, click/double-click, two-finger horizontal/vertical scroll) and Buttons (four directions, Enter, Back). Design and validate essential flows in each mode independently. Do not require PC-only Tab/Page keys, assume button-mode PDF panning is already implemented, or invent double-click/temple gesture commands.
- The normal device workflow is APK transfer/installation through Hi Rokid or AnExplorer. Physical-device installation/testing is outside the Lab; its internal ADB is private and virtual-only.

## Review before publishing

- Explain the purpose, file/folder changes and expected behavior before implementation. The user wants to understand the architecture before it grows.
- Work locally on a feature branch for review. Do not push, or integrate reviewed work into shared branches, unless the user explicitly asks. Do not treat a normal change request as authorization to publish it.

- The Lab GUI hosts a verified SDK-owned native emulator window using Windows APIs, with Start/Stop above, navigation buttons below, and Lab/App log tabs on the right. Do not attach arbitrary desktop windows. Handle native shutdown/detach before destroying a parent window.
- Send file accepts regular files into emulator Download, preserves names and chooses a numbered name on collisions. Never interpolate source filenames into shell commands, open/install sent files automatically, or migrate/delete existing app-folder PDFs without a request.

- Keep Lab ADB on its private loopback server with mDNS auto-connect disabled and the virtual-only USB filter. Reject physical transports and connect/pair commands before execution; never reuse or restart the normal PC device server.
- Configure virtual display width/height/density/font scale locally only. Do not restore hardware capture or add IP/device fields. Mouse and navigation buttons are both available; no input-mode selector is needed.
