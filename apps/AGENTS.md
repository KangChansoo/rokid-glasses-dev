# Android app modules

The user's active development path is ordinary Android APKs installed through Hi Rokid Toolbox. Do not depend on CXR-M/S licensing or undocumented Rokid APIs.

- Keep installable app modules independent. adb-helper/ opens public Settings actions only; never write secure/global settings or auto-enable ADB. Common Android UI belongs in shared/android-ui/ at the repository root. Generated output belongs in root build/, not app source folders.
- minSdk 31 targets the observed Android 12 glasses path. Do not claim hardware input, rendering, storage-provider availability or launch behavior without device evidence.
- No INTERNET, account, camera, microphone or broad storage permissions. Open a user-selected PDF through Storage Access Framework or an app-owned Documents folder. Never add MANAGE_EXTERNAL_STORAGE as an automatic workaround for a missing picker.
- Never package real papers, personal text, tokens, screenshots, logs or private signing keys. Runtime PDF copies stay on the device; backups are disabled.
- Render one page at a time off the UI thread with bounded bitmap allocation; close renderer/page/file resources, and discard stale jobs after navigation or Activity destruction.
- Preserve Android's native mouse/Enter activation and Back behavior. Do not duplicate button activation in key handlers.
- Validate with the Gradle wrapper: assembleDebug, testDebugUnitTest and lintDebug. Check all APK manifests and signatures. Label device verification separately.

- User-confirmed input modes are separate: Touchpad (pointer, click/double-click, two-finger horizontal/vertical scroll) and Buttons (four directions, Enter, Back). Design and validate essential flows in each mode independently. Do not require PC-only Tab/Page keys, assume button-mode PDF panning is already implemented, or invent double-click/temple gesture commands.
- The normal device workflow is APK transfer/installation through Hi Rokid or AnExplorer. Physical-device installation/testing is separate. The PC Lab is strictly virtual-only and never communicates with real glasses/phones.
